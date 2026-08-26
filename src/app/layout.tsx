import type { Metadata } from "next";
import { Archivo } from "next/font/google";
import "./globals.css";

const archivo = Archivo({
  subsets: ["latin"],
  weight: ["400", "600", "800"],
  variable: "--font-archivo",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Actuary — scoring a federal risk index against the losses that landed",
  description:
    "FEMA's National Risk Index assigns every US county an expected annual dollar loss and directs money accordingly. This scores it against what actually happened, out of sample, for the 71% of it that can be tested at all.",
};

const NAV = [
  ["Coverage", "#coverage"],
  ["Instruments", "#instruments"],
  ["Reversal", "#reversal"],
  ["Where it fails", "#split"],
  ["Full result", "#table"],
  ["Method", "#how"],
  ["Limits", "#limits"],
];

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={archivo.variable}>
      <body>
        <nav className="crumbs">
          {NAV.map(([label, href]) => (
            <a key={href} href={href}>
              {label}
            </a>
          ))}
          <span className="spacer" />
          <a href="https://github.com/Muhammad-Haris-3/Actuary">Repository</a>
        </nav>
        {children}
        <footer className="site">
          <div className="in">
            <span>
              National Risk Index v1.19.0 · NOAA Storm Events · NFIP claims ·
              every source open and free
            </span>
            <span>
              <a href="https://github.com/Muhammad-Haris-3/Actuary">
                Repository, data and pre-registration
              </a>
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}
