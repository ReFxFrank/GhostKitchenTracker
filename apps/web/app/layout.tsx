import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "SEANCE",
  description:
    "A public, sourced, auditable index of which delivery-app restaurant listings share a physical kitchen. New York City.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-neutral-900 antialiased flex flex-col">
        <main className="flex-1">{children}</main>
        {/* Methodology and attribution are linked from every page footer — a
            standing requirement, not a stylistic choice. */}
        <footer className="border-t border-neutral-200 px-6 py-4 text-sm text-neutral-500">
          <nav className="flex gap-6 max-w-3xl mx-auto">
            <Link href="/methodology" className="hover:text-neutral-900 underline">
              Methodology
            </Link>
            <Link href="/attribution" className="hover:text-neutral-900 underline">
              Data attribution
            </Link>
          </nav>
        </footer>
      </body>
    </html>
  );
}
