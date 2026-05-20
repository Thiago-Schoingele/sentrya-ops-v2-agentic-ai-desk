import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sentrya Ops V2",
  description: "Security and AI Operations Command Center"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
