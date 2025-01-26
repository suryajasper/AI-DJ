import Head from "next/head"; 
import { Silkscreen } from 'next/font/google';
import './globals.css';

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
      </Head>
      <body className={silkscreen.className}>
        {children}
      </body>
    </html>
  );
}
