import type { Metadata } from "next";
import { IBM_Plex_Mono, Source_Sans_3 } from "next/font/google";
import "./globals.css";

const sans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});
const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "600"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Actuary — scoring a federal risk index against the losses that landed",
  description:
    "FEMA's National Risk Index assigns every US county an expected annual dollar loss and directs money accordingly. This scores it against what actually happened, out of sample, for the 71% of it that can be tested at all.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <body>
        <div className="shell">
          <header className="site">
            <div className="in">
              <b>Actuary</b>
              <i>scoring a federal risk index against the losses that landed</i>
            </div>
          </header>
          {children}
          <footer className="site">
            <div className="in">
              <span>
                National Risk Index v1.19.0 · NOAA Storm Events · NFIP claims ·
                all sources open and free
              </span>
              <span>
                <a href="https://github.com/Muhammad-Haris-3/Actuary">
                  Repository, data and pre-registration
                </a>
              </span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
