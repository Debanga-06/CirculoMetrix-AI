import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Suspense, lazy } from 'react';

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const About = lazy(() => import('./pages/About'));
const NotFound = lazy(() => import('./pages/NotFound'));
const Navbar = lazy(() => import('./components/Navbar'));

// Loading spinner component
const Loading = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
      <p className="text-lg text-gray-600 font-medium">Loading CirculoMetrix AI...</p>
    </div>
  </div>
);

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          reverseOrder={false}
          gutter={8}
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
              padding: '16px',
              borderRadius: '8px',
              fontSize: '14px',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
            loading: {
              iconTheme: {
                primary: '#3b82f6',
                secondary: '#fff',
              },
            },
          }}
        />

        <Suspense fallback={<Loading />}>
          {/* Navigation */}
          <Navbar />

          {/* Main Content */}
          <main className="flex-grow container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/about" element={<About />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
        </Suspense>

        {/* Footer */}
        <footer className="bg-gray-800 text-white mt-auto">
          <div className="container mx-auto px-4 py-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* About Section */}
              <div>
                <h3 className="text-lg font-bold mb-4 text-white">CirculoMetrix AI</h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  AI-powered Life Cycle Assessment and Circular Economy platform
                  for sustainable metal manufacturing.
                </p>
              </div>

              {/* Quick Links */}
              <div>
                <h3 className="text-lg font-bold mb-4 text-white">Quick Links</h3>
                <ul className="space-y-2">
                  <li>
                    <a 
                      href="/dashboard" 
                      className="text-gray-300 hover:text-white transition-colors text-sm"
                    >
                      Dashboard
                    </a>
                  </li>
                  <li>
                    <a 
                      href="/about" 
                      className="text-gray-300 hover:text-white transition-colors text-sm"
                    >
                      About
                    </a>
                  </li>
                  <li>
                    <a 
                      href="https://circulometrix-ai.onrender.com/docs"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-300 hover:text-white transition-colors text-sm"
                    >
                      API Documentation
                    </a>
                  </li>
                </ul>
              </div>

              {/* Contact */}
              <div>
                <h3 className="text-lg font-bold mb-4 text-white">Contact</h3>
                <ul className="space-y-2 text-sm">
                  <li className="text-gray-300">
                    Email: squadsyntax72@gmail.com
                  </li>
                  <li className="text-gray-300">
                    Support: squadsyntax72@gmail.com
                  </li>
                  <li className="text-gray-300">
                    Phone: 7601993103 / 8389914302
                  </li>
                </ul>
              </div>
            </div>

            <div className="border-t border-gray-700 mt-8 pt-8 text-center">
              <p className="text-sm text-gray-400">
                © 2024 CirculoMetrix AI. All rights reserved.
              </p>
              <p className="text-sm text-gray-400 mt-2">
                Building a sustainable future through data-driven insights.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
