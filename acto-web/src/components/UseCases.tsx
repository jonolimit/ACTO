import { Bot, Wind, Plane, Factory, FlaskConical, Activity, ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ScrollAnimation } from './ScrollAnimation';

const useCases = [
  {
    icon: Bot,
    title: 'Robotics-as-a-Service',
    slug: 'robotics-as-a-service',
    description: 'Provide verifiable proof that your robots completed their assigned tasks. Enable trust in RaaS platforms with cryptographic execution records that customers can independently verify.'
  },
  {
    icon: Wind,
    title: 'Autonomous cleaning',
    slug: 'autonomous-cleaning',
    description: 'Document cleaning operations with tamper-proof evidence. Generate verifiable logs showing which areas were cleaned, when, and to what standard, ensuring accountability in automated facilities management.'
  },
  {
    icon: Plane,
    title: 'Drone inspections',
    slug: 'drone-inspections',
    description: 'Create immutable records of infrastructure inspections. Prove that drones followed approved flight paths, captured required imagery, and completed safety protocols without manual oversight.'
  },
  {
    icon: Factory,
    title: 'Industrial auditing',
    slug: 'industrial-auditing',
    description: 'Automate compliance verification with cryptographic audit trails. Demonstrate that automated systems performed required checks, measurements, and quality control procedures according to regulatory standards.'
  },
  {
    icon: FlaskConical,
    title: 'Research environments',
    slug: 'research-environments',
    description: 'Ensure reproducibility of automated experiments. Generate proofs that research robots executed protocols precisely as specified, enabling verification of experimental methodology and results.'
  },
  {
    icon: Activity,
    title: 'Simulation validation',
    slug: 'simulation-validation',
    description: 'Bridge the gap between simulation and reality. Prove that real-world robot behavior matches simulated models by comparing cryptographic proofs from both environments.'
  },
];

export function UseCases() {
  return (
    <section id="use-cases" className="py-16 md:py-32">
      <div className="max-w-6xl mx-auto px-4 md:px-6">
        <ScrollAnimation animation="blur-in" delay={0}>
          <h2 className="text-2xl md:text-3xl font-medium mb-4 md:mb-6 tracking-tight">Use cases</h2>
          <p className="text-base md:text-lg text-gray-600 mb-12 md:mb-16 max-w-2xl">
            From industrial automation to research, proof of execution enables trust and accountability in autonomous systems across diverse applications.
          </p>
        </ScrollAnimation>
        
        {/* Two-column layout */}
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-16 items-stretch">
          {/* Left: Image */}
          <ScrollAnimation animation="blur-in" delay={60} className="h-full">
            <div className="relative rounded-2xl overflow-hidden aspect-[4/3] lg:aspect-auto lg:h-full">
              <img 
                src="/usecases.png" 
                alt="Autonomous systems" 
                className="absolute inset-0 w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
              <div className="absolute bottom-6 left-6 right-6">
                <p className="text-white/90 text-sm font-medium">
                  Proof of execution for every industry
                </p>
              </div>
            </div>
          </ScrollAnimation>

          {/* Right: Use Cases List */}
          <div className="space-y-1">
            {useCases.map((useCase, index) => {
              const Icon = useCase.icon;
              return (
                <ScrollAnimation key={useCase.title} animation="blur-in" delay={100 + index * 50}>
                  <Link 
                    to={`/use-cases/${useCase.slug}`}
                    className="group flex items-start gap-4 p-4 -mx-4 rounded-xl hover:bg-gray-50 transition-colors duration-200"
                  >
                    <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gray-100 group-hover:bg-gray-900 transition-colors flex items-center justify-center">
                      <Icon className="w-5 h-5 text-gray-700 group-hover:text-white transition-colors" />
                    </div>
                    <div className="flex-grow min-w-0">
                      <h3 className="text-base font-medium text-gray-900 flex items-center gap-2">
                        {useCase.title}
                        <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                      </h3>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">{useCase.description}</p>
                    </div>
                  </Link>
                </ScrollAnimation>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
