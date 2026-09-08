use lettre::message::header::ContentType;
use lettre::message::{Mailbox, Message, SinglePart};
use lettre::transport::smtp::authentication::Credentials;
use lettre::AsyncSmtpTransport;
use lettre::AsyncTransport;
use lettre::Tokio1Executor;
use std::env;

#[tokio::main]
async fn main() {
    dotenvy::dotenv().ok();
    let _ = dotenvy::from_path("backend/.env");

    println!("--- TEST EMAIL SMTP GOOGLE ---");
    let host = env::var("SMTP_HOST").unwrap_or_default();
    let port: u16 = env::var("SMTP_PORT").unwrap_or_else(|_| "587".to_string()).parse().unwrap_or(587);
    let username = env::var("SMTP_USERNAME").unwrap_or_default();
    let raw_password = env::var("SMTP_PASSWORD").unwrap_or_default();
    let password = raw_password.replace(' ', "").trim().to_string();
    let from = env::var("SMTP_FROM").unwrap_or_default();
    let admin_email = env::var("SMTP_ADMIN_EMAIL").unwrap_or_default();

    println!("Host: {}", host);
    println!("Port: {}", port);
    println!("Username: {}", username);
    println!("Password length: {} (raw: '{}')", password.len(), raw_password);
    println!("From: {}", from);
    println!("Admin Email: {}", admin_email);

    if host.is_empty() || username.is_empty() || password.is_empty() {
        println!("❌ Config tidak lengkap! Host, username, atau password kosong.");
        return;
    }

    let from_mailbox: Mailbox = match from.parse() {
        Ok(mb) => mb,
        Err(e) => {
            println!("❌ Gagal parse FROM: {}", e);
            return;
        }
    };

    let to_mailbox: Mailbox = match admin_email.parse() {
        Ok(mb) => mb,
        Err(e) => {
            println!("❌ Gagal parse TO: {}", e);
            return;
        }
    };

    let creds = Credentials::new(username.clone(), password.clone());

    println!("\nMenghubungkan ke SMTP {} port {}...", host, port);

    let mailer = match AsyncSmtpTransport::<Tokio1Executor>::starttls_relay(&host) {
        Ok(builder) => builder.port(port).credentials(creds).build(),
        Err(e) => {
            println!("❌ Gagal inisialisasi transport: {:?}", e);
            return;
        }
    };

    let email = Message::builder()
        .from(from_mailbox)
        .to(to_mailbox.clone())
        .subject("[Uji Coba] Test Email Notifikasi E-Office FIT")
        .singlepart(
            SinglePart::builder()
                .header(ContentType::parse("text/html; charset=utf-8").unwrap())
                .body("<h3>Test Berhasil!</h3><p>Sistem E-Office FIT dapat mengirim email melalui Google SMTP.</p>".to_string()),
        )
        .unwrap();

    println!("Mengirim email uji coba ke {}...", admin_email);
    match mailer.send(email).await {
        Ok(response) => {
            println!("🎉 SUKSES! Email berhasil dikirim.");
            println!("SMTP Server Response: {:?}", response);
        }
        Err(e) => {
            println!("❌ GAGAL MENGIRIM EMAIL!");
            println!("Error detail: {:?}", e);
        }
    }
}
