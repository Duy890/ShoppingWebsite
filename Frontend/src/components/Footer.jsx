import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Facebook, Twitter, Instagram, Youtube, Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  const { t } = useTranslation();
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          
          {/* Brand Column */}
          <div className="space-y-6">
            <Link to="/" className="text-3xl font-extrabold tracking-tighter text-white">
              e-shop.
            </Link>
            <p className="text-sm leading-relaxed text-gray-400">
              {t('footer.description')}
            </p>
            <div className="flex space-x-4">
              <Link to="#" className="hover:text-primary transition-colors"><Facebook className="w-5 h-5" /></Link>
              <Link to="#" className="hover:text-primary transition-colors"><Twitter className="w-5 h-5" /></Link>
              <Link to="#" className="hover:text-primary transition-colors"><Instagram className="w-5 h-5" /></Link>
              <Link to="#" className="hover:text-primary transition-colors"><Youtube className="w-5 h-5" /></Link>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-bold text-lg mb-6 uppercase tracking-wider">{t('footer.shop')}</h3>
            <ul className="space-y-4 text-sm">
              <li><Link to="/products" className="hover:text-primary transition-colors">{t('footer.all_products')}</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.laptops')}</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.smartphones')}</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.audio')}</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.accessories')}</Link></li>
            </ul>
          </div>

          {/* Customer Service */}
          <div>
            <h3 className="text-white font-bold text-lg mb-6 uppercase tracking-wider">{t('footer.service')}</h3>
            <ul className="space-y-4 text-sm">
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.faq')}</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.shipping_policy')}</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.returns')}</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.privacy')}</Link></li>
              <li><Link to="#" className="hover:text-primary transition-colors">{t('footer.terms')}</Link></li>
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="text-white font-bold text-lg mb-6 uppercase tracking-wider">{t('footer.contact')}</h3>
            <ul className="space-y-4 text-sm">
              <li className="flex items-start space-x-3">
                <MapPin className="w-5 h-5 text-primary shrink-0" />
                <span>{t('footer.address')}</span>
              </li>
              <li className="flex items-center space-x-3">
                <Phone className="w-5 h-5 text-primary shrink-0" />
                <span>+1 (555) 123-4567</span>
              </li>
              <li className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-primary shrink-0" />
                <span>support@e-shop.com</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-16 pt-8 flex flex-col md:flex-row justify-between items-center text-xs text-gray-500 gap-4">
          <p>&copy; {new Date().getFullYear()} e-shop. Electronics Store. {t('footer.rights')}</p>
          <div className="flex space-x-6">
            <Link to="#" className="hover:text-gray-300">{t('footer.privacy_short')}</Link>
            <Link to="#" className="hover:text-gray-300">{t('footer.terms_short')}</Link>
            <Link to="#" className="hover:text-gray-300">{t('footer.cookies')}</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
