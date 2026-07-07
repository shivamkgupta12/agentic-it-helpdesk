import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agentic IT Helpdesk",
  description: "Multi-Agent IT Support Automation System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}