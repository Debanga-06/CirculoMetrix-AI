import { Target, Users, Award, Globe, Leaf, Brain } from 'lucide-react';

const About = () => {
  const features = [
    {
      icon: <Leaf className="w-6 h-6" />,
      title: "ISO-Compliant LCA",
      description: "Our calculations follow ISO 14040/14044 standards for accurate and reliable environmental impact assessment."
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "AI-Powered Analytics",
      description: "Machine learning algorithms analyze patterns and predict environmental impacts with high accuracy."
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Circular Economy Focus",
      description: "Built on Ellen MacArthur Foundation principles to promote circular production practices."
    }
  ];

  const team = [
    {
      name: "Sustainability Experts",
      description: "Environmental scientists with decades of LCA experience"
    },
    {
      name: "AI Engineers",
      description: "Machine learning specialists optimizing prediction models"
    },
    {
      name: "Industry Partners",
      description: "Manufacturing leaders providing real-world insights"
    }
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-full text-sm font-medium">
          <Leaf className="w-4 h-4" />
          About CirculoMetrix AI
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900">
          Building a Sustainable Future
          <br />
          <span className="text-blue-600">Through Data-Driven Insights</span>
        </h1>
        
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          CirculoMetrix AI is a comprehensive sustainability analytics platform designed 
          to help metal manufacturers measure, optimize, and report their environmental impact.
        </p>
      </section>

      {/* Mission Section */}
      <section className="bg-gradient-to-br from-blue-50 to-green-50 rounded-2xl p-8 md:p-12">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full text-sm font-medium text-blue-600">
              <Target className="w-4 h-4" />
              Our Mission
            </div>
            
            <h2 className="text-3xl font-bold text-gray-900">
              Empowering Industries to Achieve Net-Zero Goals
            </h2>
            
            <p className="text-gray-600 leading-relaxed">
              We believe that sustainable manufacturing is not just an environmental imperative 
              but also a competitive advantage. Our platform combines cutting-edge AI technology 
              with established environmental science to provide actionable insights that drive 
              real change.
            </p>
            
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-green-600 text-sm">✓</span>
                </div>
                <div>
                  <div className="font-semibold text-gray-900">Data-Driven Decisions</div>
                  <div className="text-sm text-gray-600">Make informed choices backed by accurate environmental data</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-green-600 text-sm">✓</span>
                </div>
                <div>
                  <div className="font-semibold text-gray-900">Circular Economy</div>
                  <div className="text-sm text-gray-600">Transition from linear to circular production models</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-green-600 text-sm">✓</span>
                </div>
                <div>
                  <div className="font-semibold text-gray-900">Continuous Improvement</div>
                  <div className="text-sm text-gray-600">Track progress and optimize sustainability performance over time</div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-xl p-8 space-y-6">
            <h3 className="text-2xl font-bold text-gray-900">Impact by Numbers</h3>
            
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <div className="text-3xl font-bold text-blue-600">70%</div>
                <div className="text-sm text-gray-600">Average CO₂ reduction potential</div>
              </div>
              
              <div className="border-l-4 border-green-500 pl-4">
                <div className="text-3xl font-bold text-green-600">85%</div>
                <div className="text-sm text-gray-600">Waste reduction achievable</div>
              </div>
              
              <div className="border-l-4 border-purple-500 pl-4">
                <div className="text-3xl font-bold text-purple-600">60%</div>
                <div className="text-sm text-gray-600">Energy savings possible</div>
              </div>
              
              <div className="border-l-4 border-orange-500 pl-4">
                <div className="text-3xl font-bold text-orange-600">100+</div>
                <div className="text-sm text-gray-600">Companies using our platform</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold text-gray-900">
            Why Choose CirculoMetrix AI?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Backed by science, powered by AI, designed for real-world impact
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
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

      {/* Methodology */}
      <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 md:p-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Our Methodology
        </h2>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-gray-900">
              Life Cycle Assessment (LCA)
            </h3>
            <p className="text-gray-600">
              We calculate environmental impacts across all lifecycle stages:
            </p>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>Raw material extraction and processing</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>Manufacturing and production</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>Transportation and distribution</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">•</span>
                <span>End-of-life treatment and recycling</span>
              </li>
            </ul>
          </div>

          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-gray-900">
              Material Circularity Indicator (MCI)
            </h3>
            <p className="text-gray-600">
              Based on Ellen MacArthur Foundation methodology:
            </p>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span>Virgin vs. recycled material input ratios</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span>Product utility and lifespan factors</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span>Waste generation and recycling rates</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span>Material flow efficiency metrics</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
            <Users className="w-4 h-4" />
            Our Team
          </div>
          <h2 className="text-3xl font-bold text-gray-900">
            Built by Experts, For the Industry
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {team.map((member, index) => (
            <div
              key={index}
              className="text-center p-6 bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl"
            >
              <div className="w-16 h-16 bg-blue-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {member.name}
              </h3>
              <p className="text-gray-600 text-sm">
                {member.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Standards and Certifications */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-12 text-white text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/20 rounded-full text-sm font-medium mb-6">
          <Award className="w-4 h-4" />
          Standards & Certifications
        </div>
        
        <h2 className="text-3xl font-bold mb-4">
          Trusted by Industry Leaders
        </h2>
        <p className="text-blue-100 max-w-2xl mx-auto mb-8">
          Our platform adheres to international standards and best practices
        </p>

        <div className="grid md:grid-cols-4 gap-6 text-center">
          <div className="bg-white/10 rounded-lg p-6">
            <div className="text-2xl font-bold mb-2">ISO 14040</div>
            <div className="text-sm text-blue-100">LCA Principles</div>
          </div>
          <div className="bg-white/10 rounded-lg p-6">
            <div className="text-2xl font-bold mb-2">ISO 14044</div>
            <div className="text-sm text-blue-100">LCA Requirements</div>
          </div>
          <div className="bg-white/10 rounded-lg p-6">
            <div className="text-2xl font-bold mb-2">EMF</div>
            <div className="text-sm text-blue-100">Circularity Standards</div>
          </div>
          <div className="bg-white/10 rounded-lg p-6">
            <div className="text-2xl font-bold mb-2">GHG Protocol</div>
            <div className="text-sm text-blue-100">Carbon Accounting</div>
          </div>
        </div>
      </section>

      {/* Contact CTA */}
      <section className="text-center space-y-6 py-12">
        <h2 className="text-3xl font-bold text-gray-900">
          Ready to Transform Your Manufacturing?
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Join leading manufacturers in their sustainability journey
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/dashboard"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Start Free Trial
          </a>
          <a
            href="mailto:contact@circulometrix.ai"
            className="inline-flex items-center gap-2 px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:border-blue-600 hover:text-blue-600 transition-colors"
          >
            Contact Sales
          </a>
        </div>
      </section>
    </div>
  );
};

export default About;