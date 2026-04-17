import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "One Percent Better Poker",
  description: "Post-hoc tournament performance system for serious poker players."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
