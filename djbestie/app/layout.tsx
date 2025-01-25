import Head from "next/head";  // You can use this for other meta tags if needed
import { Silkscreen } from 'next/font/google';
import './globals.css';

// Initialize the font
const silkscreen = Silkscreen({
  weight:'400'
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <Head>
        <meta name="description" content="Your description here" />
        {/* No need to manually add Google Fonts link */}
      </Head>
      <body className={silkscreen.className}>
        {children}
      </body>
    </html>
  );
}
