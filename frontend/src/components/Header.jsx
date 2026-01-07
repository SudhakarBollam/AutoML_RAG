import { Brain, Github } from 'lucide-react';

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur">
      <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-6">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold">
              AutoML Studio
            </h1>
            <p className="text-xs text-gray-500">
              Intelligent Dataset Analysis
            </p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex items-center gap-4">
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-3 py-2 text-sm rounded-md hover:bg-gray-100 transition"
          >
            <Github className="w-4 h-4 mr-2" />
            Documentation
          </a>
        </nav>
      </div>
    </header>
  );
}