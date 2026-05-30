import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/app/components/Navbar";
import Footer from "@/app/components/Footer";

export const metadata: Metadata = {
  title: "SkillScout Nusantara — Platform Pencari Kerja Berbasis AI",
  description:
    "Cocokkan CV Anda dengan lowongan kerja terbaik menggunakan AI Siamese BiLSTM. Temukan skill gap dan rekomendasi karir untuk profesional Indonesia.",
  keywords: [
    "pencari kerja",
    "AI",
    "job matching",
    "CV analysis",
    "skill gap",
    "Indonesia",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id">
      <body
        style={{
          display: "flex",
          flexDirection: "column",
          minHeight: "100vh",
        }}
      >
        <Navbar />
        <main style={{ flex: 1, paddingTop: 64 }}>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
