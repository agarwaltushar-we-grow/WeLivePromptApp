import './globals.css';

export const metadata = {
  title: 'Prompt Polisher',
  description: 'A simple bilingual prompt optimizer for English and Japanese workflows.'
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
