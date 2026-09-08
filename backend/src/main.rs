use axum::{
    extract::{Path, Query, State},
    http::{HeaderMap, StatusCode},
    response::IntoResponse,
    routing::{get, post, put},
    Json, Router,
};
use chrono::{Datelike, Local, NaiveDate};
use serde::{Deserialize, Serialize};
use sqlx::{sqlite::SqlitePoolOptions, AssertSqlSafe, FromRow, SqlitePool};
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};
use tower_http::services::{ServeDir, ServeFile};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use uuid::Uuid;

#[derive(Clone)]
struct AppState {
    dev_pool: SqlitePool,
    rooms_pool: SqlitePool,
}

// ==========================================
// MODELS
// ==========================================

#[derive(Debug, Serialize, Deserialize, FromRow)]
struct Unit {
    id: String,
    name: String,
    code: String,
    #[sqlx(rename = "signeeCode")]
    signee_code: String,
    #[sqlx(rename = "leaderName")]
    leader_name: Option<String>,
    category: String,
}

#[derive(Debug, Deserialize)]
struct CreateUnitInput {
    name: String,
    code: String,
    signee_code: Option<String>,
    leader_name: Option<String>,
    category: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, FromRow)]
struct LetterCategory {
    id: String,
    name: String,
    code: String,
    group: String,
    #[sqlx(rename = "classificationCode")]
    classification_code: Option<String>,
    description: Option<String>,
    #[sqlx(rename = "isActive")]
    is_active: bool,
}

#[derive(Debug, Deserialize)]
struct CreateCategoryInput {
    name: String,
    code: String,
    group: Option<String>,
    classification_code: Option<String>,
    description: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, FromRow)]
struct LetterResponse {
    id: String,
    #[sqlx(rename = "sequenceNumber")]
    sequence_number: i64,
    #[sqlx(rename = "monthRomawi")]
    month_romawi: Option<String>,
    month: i64,
    year: i64,
    #[sqlx(rename = "fullNumber")]
    full_number: String,
    #[sqlx(rename = "classificationCode")]
    classification_code: String,
    #[sqlx(rename = "signeeCode")]
    signee_code: String,
    subject: String,
    recipient: Option<String>,
    #[sqlx(rename = "applicantName")]
    applicant_name: String,
    #[sqlx(rename = "applicantContact")]
    applicant_contact: Option<String>,
    #[sqlx(rename = "letterDate")]
    letter_date: String,
    status: String,
    #[sqlx(rename = "isManual")]
    is_manual: bool,
    notes: Option<String>,
    #[sqlx(rename = "unitId")]
    unit_id: String,
    #[sqlx(rename = "categoryId")]
    category_id: String,
    #[sqlx(rename = "unitName")]
    unit_name: Option<String>,
    #[sqlx(rename = "categoryName")]
    category_name: Option<String>,
}

#[derive(Debug, Deserialize)]
struct GenerateLetterInput {
    #[serde(default)]
    is_manual: bool,
    manual_sequence_number: Option<i64>,
    manual_full_number: Option<String>,
    unit_id: String,
    category_id: String,
    classification_code: Option<String>,
    signee_code: Option<String>,
    subject: String,
    recipient: Option<String>,
    applicant_name: String,
    applicant_contact: Option<String>,
    letter_date: Option<String>,
    notes: Option<String>,
}

#[derive(Debug, Deserialize)]
struct UpdateLetterInput {
    subject: Option<String>,
    recipient: Option<String>,
    applicant_name: Option<String>,
    applicant_contact: Option<String>,
    status: Option<String>,
    notes: Option<String>,
}

#[derive(Debug, Deserialize)]
struct BulkDeleteInput {
    ids: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, FromRow)]
struct Room {
    id: String,
    name: String,
    code: String,
    capacity: i64,
    location: String,
    facilities: String,
    #[sqlx(rename = "priorityNotes")]
    priority_notes: Option<String>,
    #[sqlx(rename = "isCombo")]
    is_combo: bool,
    #[sqlx(rename = "comboChildCodes")]
    combo_child_codes: Option<String>,
    #[sqlx(rename = "isActive")]
    is_active: bool,
}

#[derive(Debug, Serialize, Deserialize, FromRow)]
struct RoomBookingResponse {
    id: String,
    #[sqlx(rename = "bookingNumber")]
    booking_number: String,
    #[sqlx(rename = "roomId")]
    room_id: String,
    #[sqlx(rename = "dateStr")]
    date_str: String,
    #[sqlx(rename = "startTime")]
    start_time: String,
    #[sqlx(rename = "endTime")]
    end_time: String,
    purpose: String,
    #[sqlx(rename = "unitName")]
    unit_name: String,
    #[sqlx(rename = "applicantName")]
    applicant_name: String,
    #[sqlx(rename = "applicantPhone")]
    applicant_phone: String,
    #[sqlx(rename = "participantCount")]
    participant_count: i64,
    #[sqlx(rename = "facilityNotes")]
    facility_notes: Option<String>,
    status: String,
    notes: Option<String>,
    #[sqlx(rename = "roomName")]
    room_name: Option<String>,
}

#[derive(Debug, Deserialize)]
struct CreateBookingInput {
    room_id: String,
    date_str: String,
    start_time: String,
    end_time: String,
    purpose: String,
    unit_name: String,
    applicant_name: String,
    applicant_phone: String,
    #[serde(default = "default_participants")]
    participant_count: i64,
    facility_notes: Option<String>,
}

fn default_participants() -> i64 {
    10
}

#[derive(Debug, Deserialize)]
struct UpdateBookingStatusInput {
    status: String,
    notes: Option<String>,
}

#[derive(Debug, Deserialize)]
struct CheckAvailabilityInput {
    room_id: String,
    date_str: String,
    start_time: String,
    end_time: String,
    exclude_booking_id: Option<String>,
}

#[derive(Debug, Deserialize)]
struct LetterFilters {
    limit: Option<i64>,
    offset: Option<i64>,
    search: Option<String>,
    year: Option<i64>,
    month: Option<i64>,
    unit_id: Option<String>,
    category_id: Option<String>,
    status: Option<String>,
}

#[derive(Debug, Deserialize)]
struct BookingFilters {
    limit: Option<i64>,
    offset: Option<i64>,
    search: Option<String>,
    date_str: Option<String>,
    room_id: Option<String>,
    status: Option<String>,
}

#[derive(Debug, Deserialize)]
struct AdminVerifyInput {
    pin: String,
}

// Helper Roman Month
fn get_roman_month(month: u32) -> &'static str {
    match month {
        1 => "I",
        2 => "II",
        3 => "III",
        4 => "IV",
        5 => "V",
        6 => "VI",
        7 => "VII",
        8 => "VIII",
        9 => "IX",
        10 => "X",
        11 => "XI",
        12 => "XII",
        _ => "I",
    }
}

// Partition logic MM1 + MM2 + MM_COMBO
fn get_conflicting_codes(room_code: &str) -> Vec<&'static str> {
    match room_code {
        "MM1" => vec!["MM1", "MM_COMBO"],
        "MM2" => vec!["MM2", "MM_COMBO"],
        "MM_COMBO" => vec!["MM1", "MM2", "MM_COMBO"],
        _ => vec![],
    }
}

// ==========================================
// MAIN SERVER
// ==========================================

fn resolve_sqlite_url(url: &str) -> String {
    if let Some(file_path) = url.strip_prefix("sqlite://")
        && !std::path::Path::new(file_path).exists() {
            let backend_path = format!("backend/{}", file_path);
            if std::path::Path::new(&backend_path).exists() {
                return format!("sqlite://{}", backend_path);
            }
        }
    url.to_string()
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();
    let _ = dotenvy::from_path("backend/.env");

    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "backend=info,tower_http=info".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let dev_db_url = resolve_sqlite_url(
        &std::env::var("DATABASE_URL").unwrap_or_else(|_| "sqlite://data/dev.db".to_string()),
    );
    let rooms_db_url = resolve_sqlite_url(
        &std::env::var("DATABASE_ROOMS_URL").unwrap_or_else(|_| "sqlite://data/rooms.db".to_string()),
    );

    let dev_pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&dev_db_url)
        .await?;

    let rooms_pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&rooms_db_url)
        .await?;

    let state = AppState {
        dev_pool,
        rooms_pool,
    };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let api_routes = Router::new()
        .route("/health", get(health_check))
        .route("/stats", get(get_dashboard_stats))
        .route("/admin/verify", post(verify_admin_pin))
        // Units
        .route("/units", get(get_units).post(create_unit))
        .route("/units/{id}", put(update_unit).delete(delete_unit))
        // Categories
        .route("/categories", get(get_categories).post(create_category))
        .route("/categories/{id}", put(update_category).delete(delete_category))
        // Letters
        .route("/letters", get(get_letters))
        .route("/letters/generate", post(generate_letter))
        .route("/letters/generate-batch", post(generate_batch_letters))
        .route("/agenda/verify-password", post(verify_agenda_password))
        .route("/letters/{id}", put(update_letter).delete(delete_letter))
        .route("/letters/bulk-delete", post(bulk_delete_letters))
        // Rooms & Bookings
        .route("/rooms", get(get_rooms))
        .route("/rooms/stats", get(get_room_stats))
        .route("/rooms/bookings", get(get_room_bookings).post(create_room_booking))
        .route("/rooms/check-availability", post(check_room_availability))
        .route("/rooms/bookings/{id}/status", put(update_booking_status))
        .with_state(state);

    let (dist_dir, index_html) = if std::path::Path::new("../frontend/dist").exists() {
        ("../frontend/dist", "../frontend/dist/index.html")
    } else if std::path::Path::new("frontend/dist").exists() {
        ("frontend/dist", "frontend/dist/index.html")
    } else {
        ("../frontend/dist", "../frontend/dist/index.html")
    };

    let static_service = ServeDir::new(dist_dir)
        .not_found_service(ServeFile::new(index_html));

    let app = Router::new()
        .nest("/api", api_routes)
        .fallback_service(static_service)
        .layer(cors);

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8088".to_string())
        .parse()
        .unwrap_or(8088);

    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    println!("🚀 Server FIT E-Office (Rust + Svelte) running on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

// ==========================================
// HANDLERS
// ==========================================

async fn health_check() -> impl IntoResponse {
    Json(serde_json::json!({
        "status": "ok",
        "framework": "Axum (Rust)",
        "frontend": "Svelte 5",
        "version": "1.0.0"
    }))
}

async fn verify_admin_pin(
    Json(input): Json<AdminVerifyInput>,
) -> impl IntoResponse {
    let pin = input.pin.trim();
    if pin == "admin2026" || pin == "fit2026" || pin == "vokasibangunnegeri" {
        Json(serde_json::json!({
            "success": true,
            "message": "PIN admin valid"
        }))
    } else {
        Json(serde_json::json!({
            "success": false,
            "error": "PIN yang Anda masukkan salah."
        }))
    }
}

// ------------------------------------------
// DASHBOARD STATS
// ------------------------------------------

#[derive(Serialize)]
struct DashboardStatsResponse {
    total_this_year: i64,
    total_this_month: i64,
    current_year: i32,
    current_month: u32,
    recent_letters: Vec<LetterResponse>,
    unit_stats: Vec<serde_json::Value>,
    category_stats: Vec<serde_json::Value>,
}

async fn get_dashboard_stats(
    State(state): State<AppState>,
) -> Result<Json<DashboardStatsResponse>, (StatusCode, String)> {
    let now = Local::now();
    let current_year = now.year();
    let current_month = now.month();

    let total_this_year: (i64,) = sqlx::query_as(
        r#"SELECT count(id) FROM "LetterRequest" WHERE year = ?"#,
    )
    .bind(current_year as i64)
    .fetch_one(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let total_this_month: (i64,) = sqlx::query_as(
        r#"SELECT count(id) FROM "LetterRequest" WHERE year = ? AND month = ?"#,
    )
    .bind(current_year as i64)
    .bind(current_month as i64)
    .fetch_one(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let recent_letters = sqlx::query_as::<_, LetterResponse>(
        r#"
        SELECT 
            l.id, l.sequenceNumber, l.monthRomawi, l.month, l.year, l.fullNumber,
            l.classificationCode, l.signeeCode, l.subject, l.recipient,
            l.applicantName, l.applicantContact, CASE WHEN typeof(l.letterDate) = 'integer' THEN date(l.letterDate / 1000, 'unixepoch') ELSE l.letterDate END as letterDate, l.status, l.isManual, l.notes,
            l.unitId, l.categoryId,
            u.name as unitName,
            c.name as categoryName
        FROM "LetterRequest" l
        LEFT JOIN "Unit" u ON l.unitId = u.id
        LEFT JOIN "LetterCategory" c ON l.categoryId = c.id
        ORDER BY l.createdAt DESC
        LIMIT 5
        "#,
    )
    .fetch_all(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // Group by unit
    let unit_counts: Vec<(String, i64)> = sqlx::query_as(
        r#"SELECT unitId, count(id) FROM "LetterRequest" WHERE year = ? GROUP BY unitId ORDER BY count(id) DESC LIMIT 6"#,
    )
    .bind(current_year as i64)
    .fetch_all(&state.dev_pool)
    .await
    .unwrap_or_default();

    let units = sqlx::query_as::<_, Unit>(
        r#"SELECT id, name, code, signeeCode, leaderName, category FROM "Unit""#,
    )
    .fetch_all(&state.dev_pool)
    .await
    .unwrap_or_default();

    let mut unit_stats = Vec::new();
    for (unit_id, count) in unit_counts {
        if let Some(u) = units.iter().find(|u| u.id == unit_id) {
            unit_stats.push(serde_json::json!({
                "unitId": unit_id,
                "unitName": u.name,
                "unitCode": u.code,
                "count": count
            }));
        }
    }

    // Group by category
    let category_counts: Vec<(String, i64)> = sqlx::query_as(
        r#"SELECT categoryId, count(id) FROM "LetterRequest" WHERE year = ? GROUP BY categoryId ORDER BY count(id) DESC LIMIT 6"#,
    )
    .bind(current_year as i64)
    .fetch_all(&state.dev_pool)
    .await
    .unwrap_or_default();

    let categories = sqlx::query_as::<_, LetterCategory>(
        r#"SELECT id, name, code, "group", classificationCode, description, isActive FROM "LetterCategory""#,
    )
    .fetch_all(&state.dev_pool)
    .await
    .unwrap_or_default();

    let mut category_stats = Vec::new();
    for (cat_id, count) in category_counts {
        if let Some(c) = categories.iter().find(|c| c.id == cat_id) {
            category_stats.push(serde_json::json!({
                "categoryId": cat_id,
                "categoryName": c.name,
                "categoryCode": c.code,
                "count": count
            }));
        }
    }

    Ok(Json(DashboardStatsResponse {
        total_this_year: total_this_year.0,
        total_this_month: total_this_month.0,
        current_year,
        current_month,
        recent_letters,
        unit_stats,
        category_stats,
    }))
}

// ------------------------------------------
// ROOM STATS
// ------------------------------------------

async fn get_room_stats(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let now = Local::now();
    let today_str = now.format("%Y-%m-%d").to_string();

    let total_rooms: (i64,) = sqlx::query_as(r#"SELECT count(id) FROM "Room" WHERE isActive = 1"#)
        .fetch_one(&state.rooms_pool)
        .await
        .unwrap_or((0,));

    let bookings_today: (i64,) = sqlx::query_as(
        r#"SELECT count(id) FROM "RoomBooking" WHERE dateStr = ? AND status = 'CONFIRMED'"#,
    )
    .bind(&today_str)
    .fetch_one(&state.rooms_pool)
    .await
    .unwrap_or((0,));

    let total_pending: (i64,) = sqlx::query_as(
        r#"SELECT count(id) FROM "RoomBooking" WHERE status = 'PENDING'"#,
    )
    .fetch_one(&state.rooms_pool)
    .await
    .unwrap_or((0,));

    Ok(Json(serde_json::json!({
        "totalRooms": total_rooms.0,
        "bookingsToday": bookings_today.0,
        "pendingBookings": total_pending.0,
        "todayStr": today_str
    })))
}

// ------------------------------------------
// UNITS CRUD
// ------------------------------------------

async fn get_units(
    State(state): State<AppState>,
) -> Result<Json<Vec<Unit>>, (StatusCode, String)> {
    let units = sqlx::query_as::<_, Unit>(
        r#"SELECT id, name, code, signeeCode, leaderName, category FROM "Unit" ORDER BY name ASC"#,
    )
    .fetch_all(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(units))
}

async fn create_unit(
    State(state): State<AppState>,
    Json(input): Json<CreateUnitInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let id = format!("cmt_{}", Uuid::new_v4().simple());
    let signee_code = input.signee_code.unwrap_or_else(|| "IT-DEK".to_string());
    let category = input.category.unwrap_or_else(|| "PRODI".to_string());

    sqlx::query(
        r#"INSERT INTO "Unit" (id, name, code, signeeCode, leaderName, category, updatedAt) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))"#,
    )
    .bind(&id)
    .bind(input.name.trim())
    .bind(input.code.trim().to_uppercase())
    .bind(&signee_code)
    .bind(input.leader_name.as_deref())
    .bind(&category)
    .execute(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "id": id,
        "message": "Unit berhasil ditambahkan"
    })))
}

async fn update_unit(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(input): Json<CreateUnitInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let signee_code = input.signee_code.unwrap_or_else(|| "IT-DEK".to_string());
    let category = input.category.unwrap_or_else(|| "PRODI".to_string());

    sqlx::query(
        r#"UPDATE "Unit" SET name = ?, code = ?, signeeCode = ?, leaderName = ?, category = ?, updatedAt = datetime('now') WHERE id = ?"#,
    )
    .bind(input.name.trim())
    .bind(input.code.trim().to_uppercase())
    .bind(&signee_code)
    .bind(input.leader_name.as_deref())
    .bind(&category)
    .bind(&id)
    .execute(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "message": "Unit berhasil diperbarui"
    })))
}

async fn delete_unit(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    // Cek apakah ada surat terkait
    let count: (i64,) = sqlx::query_as(r#"SELECT count(id) FROM "LetterRequest" WHERE unitId = ?"#)
        .bind(&id)
        .fetch_one(&state.dev_pool)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    if count.0 > 0 {
        return Ok(Json(serde_json::json!({
            "success": false,
            "error": "Unit tidak dapat dihapus karena masih memiliki riwayat surat yang terhubung."
        })));
    }

    sqlx::query(r#"DELETE FROM "Unit" WHERE id = ?"#)
        .bind(&id)
        .execute(&state.dev_pool)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "message": "Unit berhasil dihapus"
    })))
}

// ------------------------------------------
// CATEGORIES CRUD
// ------------------------------------------

async fn get_categories(
    State(state): State<AppState>,
) -> Result<Json<Vec<LetterCategory>>, (StatusCode, String)> {
    let categories = sqlx::query_as::<_, LetterCategory>(
        r#"SELECT id, name, code, "group", classificationCode, description, isActive FROM "LetterCategory" ORDER BY code ASC"#,
    )
    .fetch_all(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(categories))
}

async fn create_category(
    State(state): State<AppState>,
    Json(input): Json<CreateCategoryInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let id = format!("cmt_{}", Uuid::new_v4().simple());
    let group = input.group.unwrap_or_else(|| "AKD".to_string());

    sqlx::query(
        r#"INSERT INTO "LetterCategory" (id, name, code, "group", classificationCode, description, isActive, updatedAt) VALUES (?, ?, ?, ?, ?, ?, 1, datetime('now'))"#,
    )
    .bind(&id)
    .bind(input.name.trim())
    .bind(input.code.trim().to_uppercase())
    .bind(&group)
    .bind(input.classification_code.as_deref())
    .bind(input.description.as_deref())
    .execute(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "id": id,
        "message": "Kategori berhasil ditambahkan"
    })))
}

async fn update_category(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(input): Json<CreateCategoryInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let group = input.group.unwrap_or_else(|| "AKD".to_string());

    sqlx::query(
        r#"UPDATE "LetterCategory" SET name = ?, code = ?, "group" = ?, classificationCode = ?, description = ?, updatedAt = datetime('now') WHERE id = ?"#,
    )
    .bind(input.name.trim())
    .bind(input.code.trim().to_uppercase())
    .bind(&group)
    .bind(input.classification_code.as_deref())
    .bind(input.description.as_deref())
    .bind(&id)
    .execute(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "message": "Kategori berhasil diperbarui"
    })))
}

async fn delete_category(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let count: (i64,) = sqlx::query_as(r#"SELECT count(id) FROM "LetterRequest" WHERE categoryId = ?"#)
        .bind(&id)
        .fetch_one(&state.dev_pool)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    if count.0 > 0 {
        return Ok(Json(serde_json::json!({
            "success": false,
            "error": "Kategori tidak dapat dihapus karena masih digunakan oleh surat."
        })));
    }

    sqlx::query(r#"DELETE FROM "LetterCategory" WHERE id = ?"#)
        .bind(&id)
        .execute(&state.dev_pool)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "message": "Kategori berhasil dihapus"
    })))
}

// ------------------------------------------
// LETTERS
// ------------------------------------------

#[derive(Serialize)]
struct LettersListResponse {
    letters: Vec<LetterResponse>,
    total: i64,
}

async fn get_letters(
    State(state): State<AppState>,
    Query(filters): Query<LetterFilters>,
) -> Result<Json<LettersListResponse>, (StatusCode, String)> {
    let limit = filters.limit.unwrap_or(50);
    let offset = filters.offset.unwrap_or(0);

    let mut sql = String::from(
        r#"
        SELECT 
            l.id, l.sequenceNumber, l.monthRomawi, l.month, l.year, l.fullNumber,
            l.classificationCode, l.signeeCode, l.subject, l.recipient,
            l.applicantName, l.applicantContact, CASE WHEN typeof(l.letterDate) = 'integer' THEN date(l.letterDate / 1000, 'unixepoch') ELSE l.letterDate END as letterDate, l.status, l.isManual, l.notes,
            l.unitId, l.categoryId,
            u.name as unitName,
            c.name as categoryName
        FROM "LetterRequest" l
        LEFT JOIN "Unit" u ON l.unitId = u.id
        LEFT JOIN "LetterCategory" c ON l.categoryId = c.id
        WHERE 1=1
        "#,
    );

    let mut count_sql = String::from(r#"SELECT count(l.id) FROM "LetterRequest" l WHERE 1=1"#);

    if let Some(ref s) = filters.search
        && !s.trim().is_empty() {
            let part = " AND (l.fullNumber LIKE ? OR l.subject LIKE ? OR l.applicantName LIKE ? OR l.recipient LIKE ?)";
            sql.push_str(part);
            count_sql.push_str(part);
        }

    if let Some(y) = filters.year {
        let part = format!(" AND l.year = {y}");
        sql.push_str(&part);
        count_sql.push_str(&part);
    }

    if let Some(m) = filters.month {
        let part = format!(" AND l.month = {m}");
        sql.push_str(&part);
        count_sql.push_str(&part);
    }

    if let Some(ref uid) = filters.unit_id
        && !uid.trim().is_empty() && uid != "ALL" {
            let part = format!(" AND l.unitId = '{uid}'");
            sql.push_str(&part);
            count_sql.push_str(&part);
        }

    if let Some(ref st) = filters.status
        && !st.trim().is_empty() && st != "ALL" {
            let part = format!(" AND l.status = {st}");
            sql.push_str(&part);
            count_sql.push_str(&part);
        }

    if let Some(ref cid) = filters.category_id
        && !cid.trim().is_empty() && cid != "ALL" {
            let part = format!(" AND l.categoryId = '{cid}'");
            sql.push_str(&part);
            count_sql.push_str(&part);
        }

    sql.push_str(" ORDER BY l.year DESC, l.sequenceNumber DESC LIMIT ? OFFSET ?");

    // Execute count
    let total: (i64,) = if let Some(ref s) = filters.search {
        if !s.trim().is_empty() {
            let pattern = format!("%{}%", s.trim());
            sqlx::query_as(AssertSqlSafe(count_sql.as_str()))
                .bind(&pattern)
                .bind(&pattern)
                .bind(&pattern)
                .bind(&pattern)
                .fetch_one(&state.dev_pool)
                .await
                .unwrap_or((0,))
        } else {
            sqlx::query_as(AssertSqlSafe(count_sql.as_str()))
                .fetch_one(&state.dev_pool)
                .await
                .unwrap_or((0,))
        }
    } else {
        sqlx::query_as(AssertSqlSafe(count_sql.as_str()))
            .fetch_one(&state.dev_pool)
            .await
            .unwrap_or((0,))
    };

    // Execute query
    let letters: Vec<LetterResponse> = if let Some(ref s) = filters.search {
        if !s.trim().is_empty() {
            let pattern = format!("%{}%", s.trim());
            sqlx::query_as(AssertSqlSafe(sql.as_str()))
                .bind(&pattern)
                .bind(&pattern)
                .bind(&pattern)
                .bind(&pattern)
                .bind(limit)
                .bind(offset)
                .fetch_all(&state.dev_pool)
                .await
                .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
        } else {
            sqlx::query_as(AssertSqlSafe(sql.as_str()))
                .bind(limit)
                .bind(offset)
                .fetch_all(&state.dev_pool)
                .await
                .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
        }
    } else {
        sqlx::query_as(AssertSqlSafe(sql.as_str()))
            .bind(limit)
            .bind(offset)
            .fetch_all(&state.dev_pool)
            .await
            .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
    };

    Ok(Json(LettersListResponse {
        letters,
        total: total.0,
    }))
}

async fn generate_letter(
    State(state): State<AppState>,
    Json(input): Json<GenerateLetterInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    if input.unit_id.trim().is_empty()
        || input.category_id.trim().is_empty()
        || input.subject.trim().is_empty()
        || input.applicant_name.trim().is_empty()
    {
        return Ok(Json(serde_json::json!({
            "success": false,
            "error": "Semua data wajib (Unit/Prodi, Kategori, Perihal, Pemohon) harus diisi."
        })));
    }

    let parsed_date = if let Some(ref ds) = input.letter_date {
        NaiveDate::parse_from_str(ds, "%Y-%m-%d")
            .unwrap_or_else(|_| Local::now().date_naive())
    } else {
        Local::now().date_naive()
    };

    let year = parsed_date.year() as i64;
    let month = parsed_date.month() as i64;
    let month_romawi = get_roman_month(parsed_date.month());

    // Fetch Unit & Category
    let unit = sqlx::query_as::<_, Unit>(
        r#"SELECT id, name, code, signeeCode, leaderName, category FROM "Unit" WHERE id = ?"#,
    )
    .bind(&input.unit_id)
    .fetch_optional(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let category = sqlx::query_as::<_, LetterCategory>(
        r#"SELECT id, name, code, "group", classificationCode, description, isActive FROM "LetterCategory" WHERE id = ?"#,
    )
    .bind(&input.category_id)
    .fetch_optional(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let (unit, category) = match (unit, category) {
        (Some(u), Some(c)) => (u, c),
        _ => {
            return Ok(Json(serde_json::json!({
                "success": false,
                "error": "Unit atau Kategori tidak ditemukan."
            })))
        }
    };

    let active_classification = input
        .classification_code
        .as_deref()
        .filter(|s| !s.trim().is_empty())
        .unwrap_or(&category.code);

    let active_signee = input
        .signee_code
        .as_deref()
        .filter(|s| !s.trim().is_empty())
        .unwrap_or(&unit.signee_code);

    let mut tx = state.dev_pool.begin().await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let (final_seq, full_number) = if input.is_manual {
        if let Some(ref mfn) = input.manual_full_number {
            let fn_trim = mfn.trim().to_string();
            let seq = input.manual_sequence_number.unwrap_or(1);
            (seq, fn_trim)
        } else {
            let seq = input.manual_sequence_number.unwrap_or(1);
            (seq, format!("{seq}/{active_classification}/{active_signee}/{year}"))
        }
    } else {
        let last_seq: Option<(i64,)> = sqlx::query_as(
            r#"SELECT sequenceNumber FROM "LetterRequest" WHERE year = ? ORDER BY sequenceNumber DESC LIMIT 1"#,
        )
        .bind(year)
        .fetch_optional(&mut *tx)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

        let seq = last_seq.map(|s| s.0).unwrap_or(0) + 1;
        (seq, format!("{seq}/{active_classification}/{active_signee}/{year}"))
    };

    // Check duplicate fullNumber
    let dup: Option<(String, String)> = sqlx::query_as(
        r#"SELECT id, applicantName FROM "LetterRequest" WHERE fullNumber = ? LIMIT 1"#,
    )
    .bind(&full_number)
    .fetch_optional(&mut *tx)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    if let Some((_, applicant)) = dup {
        return Ok(Json(serde_json::json!({
            "success": false,
            "error": format!("Nomor surat \"{}\" sudah terdaftar di buku agenda (oleh pemohon: {}).", full_number, applicant)
        })));
    }

    let letter_id = format!("cmt_{}", Uuid::new_v4().simple());
    let date_iso = parsed_date.format("%Y-%m-%d").to_string();
    let now_ts = chrono::Utc::now().timestamp_millis();
    let letter_date_ts = parsed_date.and_hms_opt(0, 0, 0).unwrap().and_utc().timestamp_millis();

    sqlx::query(
        r#"
        INSERT INTO "LetterRequest" (
            id, sequenceNumber, monthRomawi, month, year, fullNumber,
            classificationCode, signeeCode, subject, recipient,
            applicantName, applicantContact, letterDate, notes, isManual, status,
            unitId, categoryId, createdAt, updatedAt
        ) VALUES (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?, 'ISSUED',
            ?, ?, datetime('now'), datetime('now')
        )
        "#,
    )
    .bind(&letter_id)
    .bind(final_seq)
    .bind(month_romawi)
    .bind(month)
    .bind(year)
    .bind(&full_number)
    .bind(active_classification)
    .bind(active_signee)
    .bind(input.subject.trim())
    .bind(input.recipient.as_deref().map(|s| s.trim()))
    .bind(input.applicant_name.trim())
    .bind(input.applicant_contact.as_deref().map(|s| s.trim()))
    .bind(letter_date_ts)
    .bind(input.notes.as_deref().map(|s| s.trim()))
    .bind(input.is_manual)
    .bind(&unit.id)
    .bind(&category.id).bind(now_ts).bind(now_ts)
    .execute(&mut *tx)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // Update letter counter
    sqlx::query(
        r#"
        INSERT INTO "LetterCounter" (id, year, scope, currentNumber, updatedAt)
        VALUES (?, ?, 'FIT', ?, datetime('now'))
        ON CONFLICT(year, scope) DO UPDATE SET
            currentNumber = max(currentNumber, excluded.currentNumber),
            updatedAt = datetime('now')
        "#,
    )
    .bind(format!("cnt_{}_{}", year, Uuid::new_v4().simple()))
    .bind(year)
    .bind(final_seq)
    .execute(&mut *tx)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    tx.commit().await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "letter": {
            "id": letter_id,
            "fullNumber": full_number,
            "sequenceNumber": final_seq,
            "subject": input.subject.trim(),
            "applicantName": input.applicant_name.trim(),
            "unitName": unit.name,
            "categoryName": category.name,
            "letterDate": date_iso,
            "year": year
        }
    })))
}

async fn update_letter(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(input): Json<UpdateLetterInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    sqlx::query(
        r#"
        UPDATE "LetterRequest" SET
            subject = COALESCE(?, subject),
            recipient = COALESCE(?, recipient),
            applicantName = COALESCE(?, applicantName),
            applicantContact = COALESCE(?, applicantContact),
            status = COALESCE(?, status),
            notes = COALESCE(?, notes),
            updatedAt = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(input.subject.as_deref().map(|s| s.trim()))
    .bind(input.recipient.as_deref().map(|s| s.trim()))
    .bind(input.applicant_name.as_deref().map(|s| s.trim()))
    .bind(input.applicant_contact.as_deref().map(|s| s.trim()))
    .bind(input.status.as_deref().map(|s| s.trim()))
    .bind(input.notes.as_deref().map(|s| s.trim()))
    .bind(&id)
    .execute(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "message": "Data surat berhasil diperbarui"
    })))
}

async fn delete_letter(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    sqlx::query(r#"DELETE FROM "LetterRequest" WHERE id = ?"#)
        .bind(&id)
        .execute(&state.dev_pool)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "message": "Surat berhasil dihapus"
    })))
}

async fn bulk_delete_letters(
    State(state): State<AppState>,
    Json(input): Json<BulkDeleteInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    if input.ids.is_empty() {
        return Ok(Json(serde_json::json!({
            "success": false,
            "error": "Tidak ada surat yang dipilih."
        })));
    }

    let mut count = 0;
    for id in &input.ids {
        let res = sqlx::query(r#"DELETE FROM "LetterRequest" WHERE id = ?"#)
            .bind(id)
            .execute(&state.dev_pool)
            .await;
        if res.is_ok() {
            count += 1;
        }
    }

    Ok(Json(serde_json::json!({
        "success": true,
        "deletedCount": count,
        "message": format!("{} surat berhasil dihapus", count)
    })))
}

// ------------------------------------------
// ROOMS & BOOKINGS
// ------------------------------------------

async fn get_rooms(
    State(state): State<AppState>,
) -> Result<Json<Vec<Room>>, (StatusCode, String)> {
    let rooms = sqlx::query_as::<_, Room>(
        r#"SELECT id, name, code, capacity, location, facilities, priorityNotes, isCombo, comboChildCodes, isActive FROM "Room" ORDER BY capacity ASC"#,
    )
    .fetch_all(&state.rooms_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(rooms))
}

async fn get_room_bookings(
    State(state): State<AppState>,
    headers: HeaderMap,
    Query(filters): Query<BookingFilters>,
) -> Result<Json<Vec<RoomBookingResponse>>, (StatusCode, String)> {
    let limit = filters.limit.unwrap_or(100);
    let offset = filters.offset.unwrap_or(0);

    let is_admin = headers
        .get("x-admin-pin")
        .and_then(|v| v.to_str().ok())
        .map(|p| {
            let p = p.trim();
            p == "admin2026" || p == "fit2026" || p == "vokasibangunnegeri"
        })
        .unwrap_or(false);

    let mut sql = String::from(
        r#"
        SELECT 
            b.id, b.bookingNumber, b.roomId, b.dateStr, b.startTime, b.endTime,
            b.purpose, b.unitName, b.applicantName, b.applicantPhone, b.participantCount,
            b.facilityNotes, b.status, b.notes,
            r.name as roomName
        FROM "RoomBooking" b
        LEFT JOIN "Room" r ON b.roomId = r.id
        WHERE 1=1
        "#,
    );

    if let Some(ref d) = filters.date_str
        && !d.trim().is_empty() {
            sql.push_str(&format!(" AND b.dateStr = '{d}'"));
        }

    if let Some(ref rid) = filters.room_id
        && !rid.trim().is_empty() && rid != "ALL" {
            sql.push_str(&format!(" AND b.roomId = '{rid}'"));
        }

    if let Some(ref st) = filters.status
        && !st.trim().is_empty() && st != "ALL" {
            sql.push_str(&format!(" AND b.status = '{st}'"));
        }

    if let Some(ref s) = filters.search
        && !s.trim().is_empty() {
            sql.push_str(" AND (b.bookingNumber LIKE ? OR b.purpose LIKE ? OR b.applicantName LIKE ? OR b.unitName LIKE ?)");
        }

    sql.push_str(" ORDER BY b.dateStr DESC, b.startTime ASC LIMIT ? OFFSET ?");

    let bookings: Vec<RoomBookingResponse> = if let Some(ref s) = filters.search {
        if !s.trim().is_empty() {
            let p = format!("%{}%", s.trim());
            sqlx::query_as(AssertSqlSafe(sql.as_str()))
                .bind(&p)
                .bind(&p)
                .bind(&p)
                .bind(&p)
                .bind(limit)
                .bind(offset)
                .fetch_all(&state.rooms_pool)
                .await
                .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
        } else {
            sqlx::query_as(AssertSqlSafe(sql.as_str()))
                .bind(limit)
                .bind(offset)
                .fetch_all(&state.rooms_pool)
                .await
                .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
        }
    } else {
        sqlx::query_as(AssertSqlSafe(sql.as_str()))
            .bind(limit)
            .bind(offset)
            .fetch_all(&state.rooms_pool)
            .await
            .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
    };

    let sanitized_bookings = if is_admin {
        bookings
    } else {
        bookings
            .into_iter()
            .map(|mut b| {
                b.purpose = "[Agenda Terjadwal]".to_string();
                b.applicant_name = "[Disamarkan]".to_string();
                b.applicant_phone = "-".to_string();
                b.unit_name = "[Unit Kampus]".to_string();
                b.facility_notes = None;
                b.notes = None;
                b
            })
            .collect()
    };

    Ok(Json(sanitized_bookings))
}

async fn check_room_availability(
    State(state): State<AppState>,
    Json(input): Json<CheckAvailabilityInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    if input.start_time >= input.end_time {
        return Ok(Json(serde_json::json!({
            "available": false,
            "error": "Jam selesai harus lebih besar dari jam mulai."
        })));
    }

    let target_room = sqlx::query_as::<_, Room>(
        r#"SELECT id, name, code, capacity, location, facilities, priorityNotes, isCombo, comboChildCodes, isActive FROM "Room" WHERE id = ?"#,
    )
    .bind(&input.room_id)
    .fetch_optional(&state.rooms_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let target_room = match target_room {
        Some(r) => r,
        None => {
            return Ok(Json(serde_json::json!({
                "available": false,
                "error": "Ruangan tidak ditemukan."
            })))
        }
    };

    let conflict_codes = get_conflicting_codes(&target_room.code);

    let related_rooms = if !conflict_codes.is_empty() {
        let placeholders = conflict_codes.iter().map(|_| "?").collect::<Vec<_>>().join(",");
        let q = format!(r#"SELECT id, name, code, capacity, location, facilities, priorityNotes, isCombo, comboChildCodes, isActive FROM "Room" WHERE code IN ({placeholders})"#);
        let mut query = sqlx::query_as::<_, Room>(AssertSqlSafe(q.as_str()));
        for code in conflict_codes {
            query = query.bind(code);
        }
        query.fetch_all(&state.rooms_pool).await.unwrap_or_default()
    } else {
        vec![target_room]
    };

    let related_ids: Vec<String> = related_rooms.iter().map(|r| r.id.clone()).collect();
    let id_placeholders = related_ids.iter().map(|_| "?").collect::<Vec<_>>().join(",");

    let mut q_str = format!(
        r#"
        SELECT b.id, b.bookingNumber, b.roomId, b.dateStr, b.startTime, b.endTime,
               b.purpose, b.unitName, b.applicantName, b.applicantPhone, b.participantCount,
               b.facilityNotes, b.status, b.notes, r.name as roomName
        FROM "RoomBooking" b
        LEFT JOIN "Room" r ON b.roomId = r.id
        WHERE b.dateStr = ? AND b.status = 'CONFIRMED' AND b.roomId IN ({id_placeholders})
        "#
    );

    if let Some(ref eid) = input.exclude_booking_id {
        q_str.push_str(&format!(" AND b.id != '{eid}'"));
    }

    let mut q = sqlx::query_as::<_, RoomBookingResponse>(AssertSqlSafe(q_str.as_str())).bind(&input.date_str);
    for rid in &related_ids {
        q = q.bind(rid);
    }

    let bookings = q
        .fetch_all(&state.rooms_pool)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // Check collision: startTime < b.endTime && endTime > b.startTime
    let conflict = bookings.into_iter().find(|b| {
        input.start_time < b.end_time && input.end_time > b.start_time
    });

    if let Some(c) = conflict {
        let msg = format!(
            "Jadwal bentrok! Ruangan telah terisi pada pukul {} - {} WIB. Silakan pilih jadwal waktu atau ruangan lain.",
            c.start_time, c.end_time
        );
        Ok(Json(serde_json::json!({
            "available": false,
            "error": msg,
            "conflict": {
                "roomName": c.room_name,
                "timeRange": format!("{} - {}", c.start_time, c.end_time)
            }
        })))
    } else {
        Ok(Json(serde_json::json!({
            "available": true
        })))
    }
}

async fn create_room_booking(
    State(state): State<AppState>,
    Json(input): Json<CreateBookingInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    if input.purpose.trim().is_empty()
        || input.unit_name.trim().is_empty()
        || input.applicant_name.trim().is_empty()
    {
        return Ok(Json(serde_json::json!({
            "success": false,
            "error": "Semua field bertanda bintang wajib diisi."
        })));
    }

    // Cek availability
    let check = check_room_availability(
        State(state.clone()),
        Json(CheckAvailabilityInput {
            room_id: input.room_id.clone(),
            date_str: input.date_str.clone(),
            start_time: input.start_time.clone(),
            end_time: input.end_time.clone(),
            exclude_booking_id: None,
        }),
    )
    .await?;

    let check_val: serde_json::Value = check.0;
    if check_val.get("available") != Some(&serde_json::Value::Bool(true)) {
        let err = check_val.get("error").and_then(|e| e.as_str()).unwrap_or("Jadwal bentrok.");
        return Ok(Json(serde_json::json!({
            "success": false,
            "error": err
        })));
    }

    let date_clean = input.date_str.replace('-', "");
    let count: (i64,) = sqlx::query_as(
        r#"SELECT count(id) FROM "RoomBooking" WHERE dateStr = ?"#,
    )
    .bind(&input.date_str)
    .fetch_one(&state.rooms_pool)
    .await
    .unwrap_or((0,));

    let seq = format!("{:03}", count.0 + 1);
    let booking_number = format!("BK-{date_clean}-{seq}");
    let id = format!("cmt_{}", Uuid::new_v4().simple());
    let booking_date_iso = format!("{}T{}:00", input.date_str, input.start_time);

    sqlx::query(
        r#"
        INSERT INTO "RoomBooking" (
            id, bookingNumber, roomId, bookingDate, dateStr,
            startTime, endTime, purpose, unitName, applicantName,
            applicantPhone, participantCount, facilityNotes, status,
            createdAt, updatedAt
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, 'CONFIRMED',
            datetime('now'), datetime('now')
        )
        "#,
    )
    .bind(&id)
    .bind(&booking_number)
    .bind(&input.room_id)
    .bind(&booking_date_iso)
    .bind(&input.date_str)
    .bind(&input.start_time)
    .bind(&input.end_time)
    .bind(input.purpose.trim())
    .bind(input.unit_name.trim())
    .bind(input.applicant_name.trim())
    .bind(input.applicant_phone.trim())
    .bind(input.participant_count)
    .bind(input.facility_notes.as_deref().map(|s| s.trim()))
    .execute(&state.rooms_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "booking": {
            "id": id,
            "bookingNumber": booking_number,
            "dateStr": input.date_str,
            "startTime": input.start_time,
            "endTime": input.end_time,
            "purpose": input.purpose
        }
    })))
}

async fn update_booking_status(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(input): Json<UpdateBookingStatusInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    sqlx::query(
        r#"UPDATE "RoomBooking" SET status = ?, notes = ?, updatedAt = datetime('now') WHERE id = ?"#,
    )
    .bind(input.status.trim().to_uppercase())
    .bind(input.notes.as_deref().map(|s| s.trim()))
    .bind(&id)
    .execute(&state.rooms_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "success": true,
        "message": format!("Status peminjaman berhasil diubah menjadi {}", input.status)
    })))
}


#[derive(Debug, Deserialize)]
struct VerifyPasswordInput {
    password: String,
}

async fn verify_agenda_password(
    Json(input): Json<VerifyPasswordInput>,
) -> impl IntoResponse {
    if input.password.trim() == "vokasibangunnegeri" {
        Json(serde_json::json!({ "success": true, "message": "Akses diberikan" }))
    } else {
        Json(serde_json::json!({ "success": false, "error": "Password salah. Akses ditolak." }))
    }
}

#[derive(Debug, Deserialize)]
struct BatchItemInput {
    applicant_name: Option<String>,
    recipient: Option<String>,
    subject: Option<String>,
}

#[derive(Debug, Deserialize)]
struct GenerateBatchLetterInput {
    count: usize,
    unit_id: String,
    category_id: String,
    classification_code: Option<String>,
    signee_code: Option<String>,
    subject: String,
    recipient: Option<String>,
    applicant_name: String,
    applicant_contact: Option<String>,
    letter_date: Option<String>,
    notes: Option<String>,
    items: Option<Vec<BatchItemInput>>,
}

async fn generate_batch_letters(
    State(state): State<AppState>,
    Json(input): Json<GenerateBatchLetterInput>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let total_count = input.count.clamp(1, 100);
    if input.unit_id.trim().is_empty()
        || input.category_id.trim().is_empty()
        || input.subject.trim().is_empty()
        || input.applicant_name.trim().is_empty()
    {
        return Ok(Json(serde_json::json!({
            "success": false,
            "error": "Semua data wajib harus diisi."
        })));
    }

    let parsed_date = if let Some(ref ds) = input.letter_date {
        NaiveDate::parse_from_str(ds, "%Y-%m-%d")
            .unwrap_or_else(|_| Local::now().date_naive())
    } else {
        Local::now().date_naive()
    };

    let year = parsed_date.year() as i64;
    let month = parsed_date.month() as i64;
    let month_romawi = get_roman_month(parsed_date.month());
    let letter_date_ts = parsed_date.and_hms_opt(0, 0, 0).unwrap().and_utc().timestamp_millis();
    let date_iso = parsed_date.format("%Y-%m-%d").to_string();
    let now_ts = chrono::Utc::now().timestamp_millis();

    let unit = sqlx::query_as::<_, Unit>(
        r#"SELECT id, name, code, signeeCode, leaderName, category FROM "Unit" WHERE id = ?"#,
    )
    .bind(&input.unit_id)
    .fetch_optional(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let category = sqlx::query_as::<_, LetterCategory>(
        r#"SELECT id, name, code, "group", classificationCode, description, isActive FROM "LetterCategory" WHERE id = ?"#,
    )
    .bind(&input.category_id)
    .fetch_optional(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let (unit, category) = match (unit, category) {
        (Some(u), Some(c)) => (u, c),
        _ => return Ok(Json(serde_json::json!({ "success": false, "error": "Unit atau Kategori tidak ditemukan." }))),
    };

    let active_classification = input
        .classification_code
        .as_deref()
        .filter(|s| !s.trim().is_empty())
        .unwrap_or(&category.code);

    let active_signee = input
        .signee_code
        .as_deref()
        .filter(|s| !s.trim().is_empty())
        .unwrap_or(&unit.signee_code);

    let mut tx = state.dev_pool.begin().await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let last_seq: Option<(i64,)> = sqlx::query_as(
        r#"SELECT sequenceNumber FROM "LetterRequest" WHERE year = ? ORDER BY sequenceNumber DESC LIMIT 1"#,
    )
    .bind(year)
    .fetch_optional(&mut *tx)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let start_sequence = last_seq.map(|s| s.0).unwrap_or(0) + 1;
    let mut created_letters = Vec::new();

    for i in 0..total_count {
        let current_sequence = start_sequence + (i as i64);
        let item_data = input.items.as_ref().and_then(|items| items.get(i));

        let item_subject = match item_data.and_then(|it| it.subject.as_deref()).filter(|s| !s.trim().is_empty()) {
            Some(s) => s.trim().to_string(),
            None => {
                if total_count > 1 {
                    format!("{} (Nomor #{})", input.subject.trim(), i + 1)
                } else {
                    input.subject.trim().to_string()
                }
            }
        };

        let item_recipient = item_data
            .and_then(|it| it.recipient.as_deref())
            .filter(|s| !s.trim().is_empty())
            .or_else(|| input.recipient.as_deref().filter(|s| !s.trim().is_empty()));

        let item_applicant = item_data
            .and_then(|it| it.applicant_name.as_deref())
            .filter(|s| !s.trim().is_empty())
            .unwrap_or_else(|| input.applicant_name.trim());

        let full_number = format!("{current_sequence}/{active_classification}/{active_signee}/{year}");
        let letter_id = format!("cmt_{}", Uuid::new_v4().simple());
        let item_note = input.notes.as_deref().filter(|s| !s.trim().is_empty()).map(|s| s.to_string())
            .or_else(|| if total_count > 1 { Some(format!("Batch {} Nomor (#{})", total_count, i + 1)) } else { None });

        sqlx::query(
            r#"
            INSERT INTO "LetterRequest" (
                id, sequenceNumber, monthRomawi, month, year, fullNumber,
                classificationCode, signeeCode, subject, recipient,
                applicantName, applicantContact, letterDate, notes, isManual, status,
                unitId, categoryId, createdAt, updatedAt
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, 0, 'ISSUED',
                ?, ?,
?, ?
            )
            "#,
        )
        .bind(&letter_id)
        .bind(current_sequence)
        .bind(month_romawi)
        .bind(month)
        .bind(year)
        .bind(&full_number)
        .bind(active_classification)
        .bind(active_signee)
        .bind(&item_subject)
        .bind(item_recipient)
        .bind(item_applicant)
        .bind(input.applicant_contact.as_deref().map(|s| s.trim()))
        .bind(letter_date_ts)
        .bind(item_note.as_deref())
        .bind(&unit.id)
        .bind(&category.id).bind(now_ts).bind(now_ts)
        .execute(&mut *tx)
        .await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

        created_letters.push(serde_json::json!({
            "id": letter_id,
            "fullNumber": full_number,
            "sequenceNumber": current_sequence,
            "subject": item_subject,
            "applicantName": item_applicant,
            "recipient": item_recipient,
            "letterDate": date_iso,
            "unitName": unit.name,
            "categoryName": category.name,
            "classificationCode": active_classification,
            "signeeCode": active_signee,
            "year": year
        }));
    }

    let final_sequence = start_sequence + (total_count as i64) - 1;
    sqlx::query(
        r#"
        INSERT INTO "LetterCounter" (id, year, scope, currentNumber, updatedAt)
        VALUES (?, ?, 'FIT', ?, ?)
        ON CONFLICT(year, scope) DO UPDATE SET
            currentNumber = max(currentNumber, excluded.currentNumber),
            updatedAt = excluded.updatedAt
        "#,
    )
    .bind(format!("cnt_{}_{}", year, Uuid::new_v4().simple()))
    .bind(year)
    .bind(final_sequence)
    .bind(now_ts)
    .execute(&mut *tx)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    tx.commit().await
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let start_number = format!("{start_sequence}/{active_classification}/{active_signee}/{year}");
    let end_number = format!("{final_sequence}/{active_classification}/{active_signee}/{year}");

    Ok(Json(serde_json::json!({
        "success": true,
        "count": total_count,
        "startNumber": start_number,
        "endNumber": end_number,
        "letters": created_letters
    })))
}
