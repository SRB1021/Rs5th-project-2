import "./globals.css";

export const metadata = {
  title: "TextMate",
  description: "Text and call an AI that feels like texting a real person.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-indigo-950 via-fuchsia-950 to-slate-950 text-white antialiased">
        {children}
      </body>
    </html>
  );
}
