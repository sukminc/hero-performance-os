import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "One Percent Better Poker",
  description: "Poker performance system for serious GG Poker Ontario tournament players. Track repeated patterns and get clearer next adjustments."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
