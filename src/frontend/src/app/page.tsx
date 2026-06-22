import { Dashboard } from '@/components/Dashboard';
import { Header } from '@/components/Header';

export default function Home() {
  return (
    <main className="min-h-screen">
      <Header />
      <div className="max-w-7xl mx-auto px-6 py-8">
        <Dashboard />
      </div>
    </main>
  );
}
