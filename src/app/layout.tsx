import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trade Builder - AI-Enhanced Trading Algorithm Platform",
  description: "Build, backtest, and share ML-enhanced trading algorithms. The Duolingo + Spotify of trading algorithms.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
