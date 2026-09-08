use lettre::message::header::ContentType;
use lettre::message::{Mailbox, Message, SinglePart};
use lettre::transport::smtp::authentication::Credentials;
use lettre::AsyncSmtpTransport;
use lettre::AsyncTransport;
use lettre::Tokio1Executor;
use std::env;

#[derive(Debug, Clone)]
pub struct BookingNotification {
    pub booking_number: String,
    pub room_name: String,
    pub date_str: String,
    pub start_time: String,
    pub end_time: String,
    pub purpose: String,
    pub unit_name: String,
    pub applicant_name: String,
    pub applicant_phone: String,
    pub applicant_email: Option<String>,
    pub participant_count: i64,
    pub facility_notes: Option<String>,
}

#[derive(Clone)]
struct SmtpConfig {
    host: String,
    port: u16,
    username: String,
    password: String,
    from: String,
    admin_email: Option<String>,
}

impl SmtpConfig {
    fn from_env() -> Option<Self> {
        let enabled = env::var("SMTP_ENABLED")
            .unwrap_or_else(|_| "true".to_string())
            .to_lowercase();
        if enabled == "false" || enabled == "0" {
            return None;
        }

        let host = env::var("SMTP_HOST").ok().filter(|s| !s.trim().is_empty())?;
        let port: u16 = env::var("SMTP_PORT")
            .unwrap_or_else(|_| "587".to_string())
            .parse()
            .unwrap_or(587);
        let username = env::var("SMTP_USERNAME").unwrap_or_default();
        // Google app passwords can be entered with or without spaces
        let password = env::var("SMTP_PASSWORD")
            .unwrap_or_default()
            .replace(' ', "");
        let from = env::var("SMTP_FROM")
            .unwrap_or_else(|_| "E-Office Sekre FIT <e-office@tass.telkomuniversity.ac.id>".to_string());
        let admin_email = env::var("SMTP_ADMIN_EMAIL")
            .ok()
            .filter(|s| !s.trim().is_empty());

        Some(Self {
            host,
            port,
            username,
            password,
            from,
            admin_email,
        })
    }
}

/// Tahap 1: Notifikasi saat permohonan baru diajukan (Pending Approval)
pub async fn send_submission_notifications(info: BookingNotification) {
    let config = match SmtpConfig::from_env() {
        Some(cfg) => cfg,
        None => {
            tracing::info!(
                "ℹ️ [SMTP] Konfigurasi SMTP belum aktif/lengkap di .env. Notifikasi email untuk booking {} dilewati.",
                info.booking_number
            );
            return;
        }
    };

    let from_mailbox: Mailbox = match config.from.parse() {
        Ok(mb) => mb,
        Err(e) => {
            tracing::error!("❌ [SMTP] Gagal mem-parse SMTP_FROM ({}): {}", config.from, e);
            return;
        }
    };

    let mailer = match build_transport(&config) {
        Ok(t) => t,
        Err(e) => {
            tracing::error!("❌ [SMTP] Gagal inisialisasi transport SMTP: {}", e);
            return;
        }
    };

    // 1. Email ke Pemohon: Status Pending Approval
    if let Some(ref applicant_email) = info.applicant_email {
        if !applicant_email.trim().is_empty() {
            if let Ok(to_mailbox) = applicant_email.trim().parse::<Mailbox>() {
                let subject = format!(
                    "[Menunggu Persetujuan] Peminjaman Ruangan {} - {}",
                    info.room_name, info.booking_number
                );
                let html = build_submission_applicant_html(&info);
                let email = Message::builder()
                    .from(from_mailbox.clone())
                    .to(to_mailbox)
                    .subject(subject)
                    .singlepart(
                        SinglePart::builder()
                            .header(ContentType::parse("text/html; charset=utf-8").unwrap())
                            .body(html),
                    );

                match email {
                    Ok(msg) => match mailer.send(msg).await {
                        Ok(_) => tracing::info!(
                            "✅ [SMTP] Email pending permohonan terkirim ke pemohon: {}",
                            applicant_email
                        ),
                        Err(e) => tracing::error!(
                            "❌ [SMTP] Gagal kirim email ke pemohon ({}): {}",
                            applicant_email,
                            e
                        ),
                    },
                    Err(e) => tracing::error!("❌ [SMTP] Gagal menyusun email pemohon: {}", e),
                }
            }
        }
    }

    // 2. Email ke Admin / Sekretariat: Permohonan Approval Masuk
    if let Some(ref admin_email) = config.admin_email {
        if let Ok(to_mailbox) = admin_email.trim().parse::<Mailbox>() {
            let subject = format!(
                "[Perlu Approval] Peminjaman Ruangan Baru: {} - {}",
                info.room_name, info.booking_number
            );
            let html = build_admin_approval_request_html(&info);
            let email = Message::builder()
                .from(from_mailbox.clone())
                .to(to_mailbox)
                .subject(subject)
                .singlepart(
                    SinglePart::builder()
                        .header(ContentType::parse("text/html; charset=utf-8").unwrap())
                        .body(html),
                );

            match email {
                Ok(msg) => match mailer.send(msg).await {
                    Ok(_) => tracing::info!(
                        "✅ [SMTP] Email permohonan approval terkirim ke staf sekretariat: {}",
                        admin_email
                    ),
                    Err(e) => tracing::error!(
                        "❌ [SMTP] Gagal kirim email ke sekretariat ({}): {}",
                        admin_email,
                        e
                    ),
                },
                Err(e) => tracing::error!("❌ [SMTP] Gagal menyusun email permohonan approval: {}", e),
            }
        }
    }
}

/// Tahap 2: Notifikasi keputusan setelah Staf Sekretariat melakukan Approve (CONFIRMED) atau Reject (REJECTED)
pub async fn send_approval_decision_notification(
    info: BookingNotification,
    status: String,
    notes: Option<String>,
) {
    let applicant_email = match info.applicant_email {
        Some(ref e) if !e.trim().is_empty() => e.trim().to_string(),
        _ => return, // Tidak ada email pemohon yang dituju
    };

    let config = match SmtpConfig::from_env() {
        Some(cfg) => cfg,
        None => return,
    };

    let from_mailbox: Mailbox = match config.from.parse() {
        Ok(mb) => mb,
        Err(e) => {
            tracing::error!("❌ [SMTP] Gagal mem-parse SMTP_FROM ({}): {}", config.from, e);
            return;
        }
    };

    let mailer = match build_transport(&config) {
        Ok(t) => t,
        Err(e) => {
            tracing::error!("❌ [SMTP] Gagal inisialisasi transport SMTP: {}", e);
            return;
        }
    };

    let to_mailbox: Mailbox = match applicant_email.parse() {
        Ok(mb) => mb,
        Err(e) => {
            tracing::error!("❌ [SMTP] Email pemohon tidak valid ({}): {}", applicant_email, e);
            return;
        }
    };

    let is_approved = status.eq_ignore_ascii_case("CONFIRMED");
    let subject = if is_approved {
        format!(
            "[Disetujui] Peminjaman Ruangan {} - {}",
            info.room_name, info.booking_number
        )
    } else {
        format!(
            "[Ditolak] Peminjaman Ruangan {} - {}",
            info.room_name, info.booking_number
        )
    };

    let html = build_decision_html(&info, is_approved, notes.as_deref());
    let email = Message::builder()
        .from(from_mailbox)
        .to(to_mailbox)
        .subject(subject)
        .singlepart(
            SinglePart::builder()
                .header(ContentType::parse("text/html; charset=utf-8").unwrap())
                .body(html),
        );

    match email {
        Ok(msg) => match mailer.send(msg).await {
            Ok(_) => tracing::info!(
                "✅ [SMTP] Email notifikasi keputusan ({}) terkirim ke pemohon: {}",
                status,
                applicant_email
            ),
            Err(e) => tracing::error!(
                "❌ [SMTP] Gagal kirim email keputusan ke pemohon ({}): {}",
                applicant_email,
                e
            ),
        },
        Err(e) => tracing::error!("❌ [SMTP] Gagal menyusun email keputusan: {}", e),
    }
}

fn build_transport(
    cfg: &SmtpConfig,
) -> Result<AsyncSmtpTransport<Tokio1Executor>, lettre::transport::smtp::Error> {
    let mut builder = if cfg.port == 465 {
        AsyncSmtpTransport::<Tokio1Executor>::relay(&cfg.host)?
            .port(cfg.port)
    } else {
        AsyncSmtpTransport::<Tokio1Executor>::starttls_relay(&cfg.host)?
            .port(cfg.port)
    };

    if !cfg.username.is_empty() && !cfg.password.is_empty() {
        let creds = Credentials::new(cfg.username.clone(), cfg.password.clone());
        builder = builder.credentials(creds);
    }

    Ok(builder.build())
}

fn build_details_table(info: &BookingNotification) -> String {
    let facility_row = if let Some(ref notes) = info.facility_notes {
        if !notes.trim().is_empty() {
            format!(
                r#"<tr>
                    <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px; width: 35%;">Catatan Fasilitas</td>
                    <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 500;">{}</td>
                </tr>"#,
                escape_html(notes)
            )
        } else {
            String::new()
        }
    } else {
        String::new()
    };

    let email_row = if let Some(ref email) = info.applicant_email {
        if !email.trim().is_empty() {
            format!(
                r#"<tr>
                    <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px; width: 35%;">Email Pemohon</td>
                    <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 500;">{}</td>
                </tr>"#,
                escape_html(email)
            )
        } else {
            String::new()
        }
    } else {
        String::new()
    };

    format!(
        r#"<table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse; background-color: #f8fafc; border-radius: 8px; overflow: hidden; border: 1px solid #f1f5f9; margin-bottom: 24px;">
          <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px; width: 35%;">Nomor Booking</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0284c7; font-size: 14px; font-weight: 700;">{}</td>
          </tr>
          <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px;">Ruangan</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 600;">{}</td>
          </tr>
          <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px;">Tanggal</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 500;">{}</td>
          </tr>
          <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px;">Waktu</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 500;">{} - {} WIB</td>
          </tr>
          <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px;">Keperluan</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 500;">{}</td>
          </tr>
          <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px;">Unit / Prodi</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 500;">{}</td>
          </tr>
          <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px;">Pemohon (PIC)</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 500;">{} ({})</td>
          </tr>
          {}
          <tr>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #64748b; font-size: 14px;">Peserta</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; color: #0f172a; font-size: 14px; font-weight: 500;">{} Orang</td>
          </tr>
          {}
        </table>"#,
        escape_html(&info.booking_number),
        escape_html(&info.room_name),
        escape_html(&info.date_str),
        escape_html(&info.start_time),
        escape_html(&info.end_time),
        escape_html(&info.purpose),
        escape_html(&info.unit_name),
        escape_html(&info.applicant_name),
        escape_html(&info.applicant_phone),
        email_row,
        info.participant_count,
        facility_row
    )
}

fn build_submission_applicant_html(info: &BookingNotification) -> String {
    let details_table = build_details_table(info);
    format!(
        r#"<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Peminjaman Ruangan Diajukan</title>
</head>
<body style="margin: 0; padding: 24px; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
    <tr>
      <td style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); padding: 28px 24px; text-align: center;">
        <h2 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 700;">Layanan Sekretariat FIT</h2>
        <p style="margin: 6px 0 0 0; color: #e0f2fe; font-size: 14px;">E-Office &amp; Manajemen Ruangan</p>
      </td>
    </tr>

    <tr>
      <td style="padding: 24px 28px;">
        <div style="background-color: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
          <span style="color: #92400e; font-size: 14px; font-weight: 600;">⏳ Status: MENUNGGU PERSETUJUAN (PENDING APPROVAL)</span>
        </div>

        <p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: #334155;">
          Halo <strong>{}</strong>, permohonan peminjaman ruangan Anda telah berhasil tercatat di sistem kami dan saat ini <strong>sedang menunggu persetujuan (approval)</strong> dari Staf Sekretariat FIT.
        </p>
        <p style="margin: 0 0 20px 0; font-size: 14px; line-height: 1.5; color: #64748b;">
          Anda akan menerima email pemberitahuan lanjutan setelah staf sekretariat memverifikasi dan menyetujui jadwal tersebut.
        </p>

        {}

        <div style="font-size: 13px; color: #64748b; line-height: 1.5; border-top: 1px solid #e2e8f0; padding-top: 16px;">
          <p style="margin: 0 0 4px 0;"><strong>Catatan:</strong></p>
          <p style="margin: 0;">Jika ada urgensi atau pertanyaan terkait permohonan ini, silakan hubungi tim Sekretariat FIT Telkom University.</p>
        </div>
      </td>
    </tr>

    <tr>
      <td style="background-color: #f1f5f9; padding: 18px 24px; text-align: center; border-top: 1px solid #e2e8f0;">
        <p style="margin: 0; font-size: 12px; color: #64748b;">
          Email ini dikirim otomatis oleh Sistem Layanan Sekretariat FIT Telkom University.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>"#,
        escape_html(&info.applicant_name),
        details_table
    )
}

fn build_admin_approval_request_html(info: &BookingNotification) -> String {
    let details_table = build_details_table(info);
    format!(
        r#"<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Permohonan Peminjaman Ruangan Baru</title>
</head>
<body style="margin: 0; padding: 24px; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
    <tr>
      <td style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); padding: 28px 24px; text-align: center;">
        <h2 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 700;">Layanan Sekretariat FIT</h2>
        <p style="margin: 6px 0 0 0; color: #e0f2fe; font-size: 14px;">Pemberitahuan Staf Sekretariat</p>
      </td>
    </tr>

    <tr>
      <td style="padding: 24px 28px;">
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
          <span style="color: #991b1b; font-size: 14px; font-weight: 600;">🔔 PERMOHONAN BARU MEMERLUKAN APPROVAL</span>
        </div>

        <p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: #334155;">
          Terdapat permohonan peminjaman ruangan baru dari <strong>{}</strong> (Unit/Prodi: <strong>{}</strong>) yang memerlukan persetujuan dari Staf Sekretariat.
        </p>

        {}

        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; text-align: center; margin-top: 20px;">
          <p style="margin: 0 0 8px 0; font-size: 13px; color: #475569; font-weight: 500;">
            Silakan buka dashboard E-Office Sekretariat untuk melakukan verifikasi dan persetujuan:
          </p>
          <a href="http://localhost:5173" style="display: inline-block; background-color: #0284c7; color: #ffffff; text-decoration: none; font-size: 13px; font-weight: 600; padding: 8px 20px; border-radius: 8px; margin-top: 4px;">
            Buka Menu Ruangan (Admin Staf Sekretariat)
          </a>
        </div>
      </td>
    </tr>

    <tr>
      <td style="background-color: #f1f5f9; padding: 18px 24px; text-align: center; border-top: 1px solid #e2e8f0;">
        <p style="margin: 0; font-size: 12px; color: #64748b;">
          Email ini dikirim otomatis ke tim Sekretariat FIT Telkom University.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>"#,
        escape_html(&info.applicant_name),
        escape_html(&info.unit_name),
        details_table
    )
}

fn build_decision_html(
    info: &BookingNotification,
    is_approved: bool,
    notes: Option<&str>,
) -> String {
    let details_table = build_details_table(info);

    let (badge_bg, badge_border, badge_color, badge_text, greeting_text) = if is_approved {
        (
            "#f0fdf4",
            "#bbf7d0",
            "#166534",
            "✅ Status: DISETUJUI (CONFIRMED)",
            format!(
                "Kabar baik! Permohonan peminjaman ruangan Anda telah <strong>disetujui</strong> oleh Staf Sekretariat FIT.",
            ),
        )
    } else {
        (
            "#fef2f2",
            "#fecaca",
            "#991b1b",
            "❌ Status: TIDAK DISETUJUI / DITOLAK (REJECTED)",
            format!(
                "Mohon maaf, permohonan peminjaman ruangan Anda <strong>belum dapat disetujui</strong> oleh Staf Sekretariat FIT.",
            ),
        )
    };

    let notes_block = if let Some(n) = notes {
        if !n.trim().is_empty() {
            format!(
                r#"<div style="background-color: #f8fafc; border-left: 4px solid {}; padding: 12px 16px; margin: 16px 0; border-radius: 4px;">
                  <strong style="font-size: 13px; color: #334155;">Catatan dari Staf Sekretariat:</strong>
                  <p style="margin: 4px 0 0 0; font-size: 14px; color: #475569;">{}</p>
                </div>"#,
                if is_approved { "#22c55e" } else { "#ef4444" },
                escape_html(n.trim())
            )
        } else {
            String::new()
        }
    } else {
        String::new()
    };

    let guidelines = if is_approved {
        r#"<div style="font-size: 13px; color: #64748b; line-height: 1.5; border-top: 1px solid #e2e8f0; padding-top: 16px;">
          <p style="margin: 0 0 4px 0;"><strong>Tata Tertib Penggunaan Ruangan:</strong></p>
          <ul style="margin: 0; padding-left: 18px;">
            <li>Harap menjaga kebersihan dan ketertiban ruangan selama dan setelah kegiatan.</li>
            <li>Pastikan seluruh peralatan elektronik (AC, proyektor, lampu) dimatikan setelah selesai.</li>
            <li>Kunci ruangan dapat diambil di Sekretariat FIT menjelang kegiatan berlangsung.</li>
          </ul>
        </div>"#
    } else {
        r#"<div style="font-size: 13px; color: #64748b; line-height: 1.5; border-top: 1px solid #e2e8f0; padding-top: 16px;">
          <p style="margin: 0;">Silakan mengajukan jadwal alternatif atau menghubungi Sekretariat FIT jika membutuhkan informasi lebih lanjut.</p>
        </div>"#
    };

    format!(
        r#"<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <title>Status Peminjaman Ruangan</title>
</head>
<body style="margin: 0; padding: 24px; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0;">
    <tr>
      <td style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); padding: 28px 24px; text-align: center;">
        <h2 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 700;">Layanan Sekretariat FIT</h2>
        <p style="margin: 6px 0 0 0; color: #e0f2fe; font-size: 14px;">E-Office &amp; Manajemen Ruangan</p>
      </td>
    </tr>

    <tr>
      <td style="padding: 24px 28px;">
        <div style="background-color: {}; border: 1px solid {}; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
          <span style="color: {}; font-size: 14px; font-weight: 600;">{}</span>
        </div>

        <p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: #334155;">
          Halo <strong>{}</strong>, {}
        </p>

        {}

        {}

        {}
      </td>
    </tr>

    <tr>
      <td style="background-color: #f1f5f9; padding: 18px 24px; text-align: center; border-top: 1px solid #e2e8f0;">
        <p style="margin: 0; font-size: 12px; color: #64748b;">
          Email ini dikirim otomatis oleh Sistem Layanan Sekretariat FIT Telkom University.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>"#,
        badge_bg,
        badge_border,
        badge_color,
        badge_text,
        escape_html(&info.applicant_name),
        greeting_text,
        notes_block,
        details_table,
        guidelines
    )
}

fn escape_html(input: &str) -> String {
    input
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}
