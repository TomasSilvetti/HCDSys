import HeroSection from '../components/sections/HeroSection';
import FeaturesSection from '../components/sections/FeaturesSection';
import DocumentTypesSection from '../components/sections/DocumentTypesSection';
import CtaSection from '../components/sections/CtaSection';

const HomePage = () => {
  return (
    <div className="space-y-12 pb-8">
      <HeroSection />
      <FeaturesSection />
      <DocumentTypesSection />
      <CtaSection />
    </div>
  );
};

export default HomePage;