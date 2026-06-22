import Link from 'next/link';

export function Header() {
  return (
    <header className="border-b border-kinz-100 bg-white/70 backdrop-blur sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-kinz-500 text-white grid place-items-center font-serif text-lg">
            K
          </div>
          <div>
            <h1 className="font-serif text-xl text-kinz-700 leading-tight">KINZ</h1>
            <p className="text-xs text-kinz-400">Secure Commerce Hub</p>
          </div>
        </div>
        <nav className="flex items-center gap-6 text-sm text-kinz-600">
          <Link href="/" className="hover:text-kinz-800">Dashboard</Link>
          <Link href="/products" className="hover:text-kinz-800">Products</Link>
          <Link href="/analytics" className="hover:text-kinz-800">Analytics</Link>
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="ml-2 px-3 py-1.5 rounded-lg bg-kinz-500 text-white hover:bg-kinz-600"
          >
            API Docs
          </a>
        </nav>
      </div>
    </header>
  );
}
