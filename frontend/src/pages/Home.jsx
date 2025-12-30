import { Link } from 'react-router-dom';
import { 
  Leaf, 
  TrendingDown, 
  Recycle, 
  Brain, 
  BarChart3, 
  FileText,
  ArrowRight,
  CheckCircle
} from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Life Cycle Assessment",
      description: "Comprehensive LCA calculations based on ISO 14040/14044 standards for accurate environmental impact analysis."
    },
    {
      icon: <Recycle className="w-8 h-8" />,
      title: "Circular Economy Metrics",
      description: "Calculate Material Circularity Indicator (MCI) and track your journey towards circular production."
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: "AI-Powered Predictions",
      description: "Machine learning models predict environmental impacts and optimize your production parameters."
    },
    {
      icon: <TrendingDown className="w-8 h-8" />,
      title: "Smart Recommendations",
      description: "Get actionable recommendations to reduce emissions, save energy, and improve sustainability."
    },
    {
      icon: <Leaf className="w-8 h-8" />,
      title: "What-If Scenarios",
      description: "Test different scenarios and compare their environmental impacts before implementation."
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: "Professional Reports",
      description: "Generate comprehensive PDF reports for stakeholders, investors, and regulatory compliance."
    }
  ];

  const stats = [
    { value: "95%", label: "CO₂ Reduction Potential" },
    { value: "60%", label: "Energy Savings" },
    { value: "85%", label: "Waste Reduction" },
    { value: "3+", label: "Materials Supported" }
  ];

  const benefits = [
    "Reduce carbon footprint by up to 70%",
    "Comply with environmental regulations",
    "Optimize resource utilization",
    "Improve brand sustainability image",
    "Make data-driven decisions",
    "Track progress over time"
  ];

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="text-center space-y-8 py-12">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
          <Leaf className="w-4 h-4" />
          AI-Powered Sustainability Analytics
        </div>
        
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 leading-tight">
          Transform Your Manufacturing
          <br />
          <span className="text-blue-600">Into Sustainable Production</span>
        </h1>
        
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          CirculoMetrix AI combines Life Cycle Assessment, Circular Economy principles, 
          and Machine Learning to help metal manufacturers achieve their sustainability goals.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-lg"
          >
            Get Started
            <ArrowRight className="w-5 h-5" />
          </Link>
          
          <a
            href="https://circulometrix-ai.onrender.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:border-blue-600 hover:text-blue-600 transition-colors"
          >
            View API Docs
          </a>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-blue-600 text-white rounded-2xl p-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl md:text-5xl font-bold mb-2">
                {stat.value}
              </div>
              <div className="text-blue-100 text-sm md:text-base">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-4xl font-bold text-gray-900">
            Powerful Features for Sustainable Manufacturing
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Everything you need to measure, analyze, and improve your environmental impact
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mb-4">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-gradient-to-br from-green-50 to-blue-50 rounded-2xl p-12">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h2 className="text-4xl font-bold text-gray-900">
              Why Choose CirculoMetrix AI?
            </h2>
            <p className="text-lg text-gray-600">
              Join leading manufacturers in their journey towards sustainable production 
              with our comprehensive sustainability analytics platform.
            </p>
            
            <div className="space-y-3">
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-start gap-3">
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{benefit}</span>
                </div>
              ))}
            </div>

            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Start Your Analysis
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>

          <div className="bg-white rounded-xl shadow-xl p-8 space-y-6">
            <h3 className="text-2xl font-bold text-gray-900">
              Supported Materials
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-semibold text-gray-900">Aluminum / Aluminium</div>
                  <div className="text-sm text-gray-600">Primary & Secondary Production</div>
                </div>
                <div className="text-blue-600 font-bold">✓</div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-semibold text-gray-900">Copper</div>
                  <div className="text-sm text-gray-600">Refined & Recycled</div>
                </div>
                <div className="text-blue-600 font-bold">✓</div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-semibold text-gray-900">Steel</div>
                  <div className="text-sm text-gray-600">Virgin & Scrap-based</div>
                </div>
                <div className="text-blue-600 font-bold">✓</div>
              </div>
            </div>

            <p className="text-sm text-gray-500 text-center pt-4 border-t">
              More materials coming soon
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="text-center space-y-8 py-12 bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl text-white">
        <h2 className="text-4xl font-bold">
          Ready to Start Your Sustainability Journey?
        </h2>
        <p className="text-xl text-blue-100 max-w-2xl mx-auto">
          Calculate your first LCA analysis in minutes and get actionable recommendations 
          to reduce your environmental impact.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-lg"
        >
          Launch Dashboard
          <ArrowRight className="w-5 h-5" />
        </Link>
      </section>

      {/* How It Works */}
      <section className="space-y-12">
        <div className="text-center space-y-4">
          <h2 className="text-4xl font-bold text-gray-900">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get started in three simple steps
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
              1
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              Input Your Data
            </h3>
            <p className="text-gray-600">
              Enter your production parameters including material type, quantity, 
              energy source, and recycling rates.
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
              2
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              AI Analysis
            </h3>
            <p className="text-gray-600">
              Our AI engine calculates LCA metrics, circularity scores, and 
              generates personalized recommendations.
            </p>
          </div>

          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
              3
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              Take Action
            </h3>
            <p className="text-gray-600">
              Implement recommendations, track improvements, and generate 
              professional reports for stakeholders.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
