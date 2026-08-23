import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ParcelPilot AI Support Agent",
  description: "Enterprise Logistics & Parcel Support AI Assistant",
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/icon.png", type: "image/png" }
    ],
    shortcut: "/icon.png",
    apple: "/icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.png" type="image/png" />
        <link rel="apple-touch-icon" href="/icon.png" />
        <link rel="shortcut icon" href="/icon.png" />
      </head>
      <body className="h-full flex flex-col overflow-hidden">
        {children}
      </body>
    </html>
  );
}
