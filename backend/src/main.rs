use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::get,
    Json, Router,
};
use serde::{Deserialize, Serialize};
use sqlx::{sqlite::SqlitePoolOptions, FromRow, SqlitePool};
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};
use tower_http::services::{ServeDir, ServeFile};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Clone)]
struct AppState {
    dev_pool: SqlitePool,
    rooms_pool: SqlitePool,
}

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

#[derive(Debug, Serialize, Deserialize, FromRow)]
struct LetterResponse {
    id: String,
    #[sqlx(rename = "sequenceNumber")]
    sequence_number: i64,
    #[sqlx(rename = "fullNumber")]
    full_number: String,
    subject: String,
    recipient: Option<String>,
    #[sqlx(rename = "applicantName")]
    applicant_name: String,
    #[sqlx(rename = "applicantContact")]
    applicant_contact: Option<String>,
    status: String,
    year: i64,
    month: i64,
    #[sqlx(rename = "unitName")]
    unit_name: Option<String>,
    #[sqlx(rename = "categoryName")]
    category_name: Option<String>,
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
    status: String,
    #[sqlx(rename = "roomName")]
    room_name: Option<String>,
}

#[derive(Debug, Deserialize)]
struct Pagination {
    limit: Option<i64>,
    offset: Option<i64>,
    search: Option<String>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenvy::dotenv().ok();

    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "backend=debug,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let dev_db_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "sqlite://data/dev.db".to_string());
    let rooms_db_url = std::env::var("DATABASE_ROOMS_URL")
        .unwrap_or_else(|_| "sqlite://data/rooms.db".to_string());

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
        .route("/units", get(get_units))
        .route("/categories", get(get_categories))
        .route("/letters", get(get_letters))
        .route("/rooms", get(get_rooms))
        .route("/rooms/bookings", get(get_room_bookings))
        .with_state(state);

    let static_service = ServeDir::new("../frontend/dist")
        .not_found_service(ServeFile::new("../frontend/dist/index.html"));

    let app = Router::new()
        .nest("/api", api_routes)
        .fallback_service(static_service)
        .layer(cors);

    let port: u16 = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .unwrap_or(8080);

    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    println!("🚀 Server FIT E-Office (Rust + Svelte) running on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn health_check() -> impl IntoResponse {
    Json(serde_json::json!({
        "status": "ok",
        "framework": "Axum (Rust)",
        "frontend": "Svelte 5",
        "version": "0.1.0"
    }))
}

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

async fn get_letters(
    State(state): State<AppState>,
    Query(params): Query<Pagination>,
) -> Result<Json<Vec<LetterResponse>>, (StatusCode, String)> {
    let limit = params.limit.unwrap_or(50);
    let offset = params.offset.unwrap_or(0);

    let letters = sqlx::query_as::<_, LetterResponse>(
        r#"
        SELECT 
            l.id, l.sequenceNumber, l.fullNumber, l.subject, l.recipient,
            l.applicantName, l.applicantContact, l.status, l.year, l.month,
            u.name as unitName,
            c.name as categoryName
        FROM "LetterRequest" l
        LEFT JOIN "Unit" u ON l.unitId = u.id
        LEFT JOIN "LetterCategory" c ON l.categoryId = c.id
        ORDER BY l.year DESC, l.sequenceNumber DESC
        LIMIT ? OFFSET ?
        "#,
    )
    .bind(limit)
    .bind(offset)
    .fetch_all(&state.dev_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(letters))
}

async fn get_rooms(
    State(state): State<AppState>,
) -> Result<Json<Vec<Room>>, (StatusCode, String)> {
    let rooms = sqlx::query_as::<_, Room>(
        r#"SELECT id, name, code, capacity, location, facilities, priorityNotes, isCombo, isActive FROM "Room" ORDER BY capacity ASC"#,
    )
    .fetch_all(&state.rooms_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(rooms))
}

async fn get_room_bookings(
    State(state): State<AppState>,
    Query(params): Query<Pagination>,
) -> Result<Json<Vec<RoomBookingResponse>>, (StatusCode, String)> {
    let limit = params.limit.unwrap_or(50);
    let offset = params.offset.unwrap_or(0);

    let bookings = sqlx::query_as::<_, RoomBookingResponse>(
        r#"
        SELECT 
            b.id, b.bookingNumber, b.roomId, b.dateStr, b.startTime, b.endTime,
            b.purpose, b.unitName, b.applicantName, b.applicantPhone, b.participantCount,
            b.status,
            r.name as roomName
        FROM "RoomBooking" b
        LEFT JOIN "Room" r ON b.roomId = r.id
        ORDER BY b.dateStr DESC, b.startTime ASC
        LIMIT ? OFFSET ?
        "#,
    )
    .bind(limit)
    .bind(offset)
    .fetch_all(&state.rooms_pool)
    .await
    .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(bookings))
}
