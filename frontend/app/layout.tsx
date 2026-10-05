import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Retail Fulfillment Failure Reason Classification',
  description: 'Fulfillment failure supervisor dashboard and AI classification workflow.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
