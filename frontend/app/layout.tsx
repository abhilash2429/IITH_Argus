'use client';

import './globals.css';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_LINKS = [
  { href: '/upload', label: 'Upload' },
  { href: '/notes', label: 'Notes' },
  { href: '/pipeline', label: 'Pipeline' },
  { href: '/results', label: 'Results' },
  { href: '/explain', label: 'Explain' },
  { href: '/chat', label: 'Chat' },
  { href: '/cam', label: 'CAM' },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <html lang="en">
      <head>
        <title>InsightCredit | AI Credit Appraisal</title>
        <meta name="description" content="AI-powered Credit Appraisal Engine for Indian Corporate Lending" />
      </head>
      <body className="bg-ic-page text-ic-text antialiased">
        {/* Sticky Navbar */}
        <nav className="sticky top-0 z-50 h-14 bg-ic-surface border-b border-ic-border backdrop-blur-sm flex items-center px-8">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-0.5 shrink-0 no-underline">
            <span className="font-display text-lg font-normal text-ic-text">Insight</span>
            <span className="font-display text-lg font-semibold text-ic-accent">Credit</span>
          </Link>

          {/* Centre nav links */}
          <div className="flex-1 flex items-center justify-center gap-6">
            {NAV_LINKS.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-[13px] font-medium no-underline pb-0.5 transition-colors ${
                    isActive
                      ? 'text-ic-accent border-b-2 border-ic-accent'
                      : 'text-ic-muted hover:text-ic-text'
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Right button */}
          <Link
            href="/cam"
            className="shrink-0 px-4 py-1.5 bg-ic-accent text-white text-xs font-medium rounded-md no-underline hover:opacity-90 transition-opacity"
          >
            Export Memo →
          </Link>
        </nav>

        {/* Page content */}
        <main className="min-h-[calc(100vh-56px)] overflow-y-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
