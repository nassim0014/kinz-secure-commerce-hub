import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'KINZ Secure Commerce Hub',
  description: 'Security-first e-commerce intelligence dashboard for KINZ — Tunisian natural cosmetics & vegetable oils.',
  metadataBase: new URL('https://kinz-secure-commerce-hub.vercel.app'),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
