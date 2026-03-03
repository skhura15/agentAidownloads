/**
 * Header Component
 * 
 * Sticky navigation header with HCLTech branding, navigation menu, and CTA button.
 * Features:
 * - Responsive design with mobile hamburger menu
 * - Smooth scroll to sections
 * - Shadow effect on scroll
 * - Active link highlighting
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, ChevronDown } from 'lucide-react';
import { theme } from '../styles/theme';

interface NavItem {
  label: string;
  href: string;
  isExternal?: boolean;
  dropdown?: { label: string; href: string }[];
}

const Header: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Navigation items
  const navItems: NavItem[] = [
    { label: 'Home', href: '/' },
    { 
      label: 'AI Agents', 
      href: '/agents',
      dropdown: [
        { label: 'All Agents', href: '/agents' },
        { label: 'Customer Service', href: '/agents?category=customer-service' },
        { label: 'Analytics', href: '/agents?category=analytics' },
        { label: 'Operations', href: '/agents?category=operations' },
      ]
    },
    { label: 'Documentation', href: '/docs' },
    { label: 'About', href: '/about' },
  ];

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
    setActiveDropdown(null);
  }, [location]);

  // Handle navigation
  const handleNavClick = (href: string, e: React.MouseEvent) => {
    e.preventDefault();
    
    // If it's a hash link on the landing page
    if (href.startsWith('/#')) {
      const id = href.substring(2);
      if (location.pathname === '/') {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      } else {
        navigate('/');
        setTimeout(() => {
          document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    } else {
      navigate(href);
    }
  };

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        left: 0,
        right: 0,
        zIndex: theme.zIndex.sticky,
        backgroundColor: isScrolled ? 'rgba(255, 255, 255, 0.95)' : theme.colors.white,
        backdropFilter: isScrolled ? 'blur(10px)' : 'none',
        boxShadow: isScrolled ? theme.shadows.md : 'none',
        transition: `all ${theme.transitions.base}`,
      }}
    >
      <nav
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          padding: '1rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Logo */}
        <Link
          to="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            textDecoration: 'none',
          }}
        >
          <img
            src="/assets/hcltech-logo.png"
            alt="HCLTech Logo"
            style={{
              height: '40px',
              width: 'auto',
            }}
            onError={(e) => {
              // Fallback if logo not found
              e.currentTarget.style.display = 'none';
              const fallback = document.createElement('div');
              fallback.style.cssText = `
                font-family: ${theme.typography.fontHeading};
                font-size: ${theme.typography.fontSize['2xl']};
                font-weight: ${theme.typography.fontWeight.bold};
                color: ${theme.colors.primary};
              `;
              fallback.textContent = 'HCLTech';
              e.currentTarget.parentElement?.appendChild(fallback);
            }}
          />
        </Link>

        {/* Desktop Navigation */}
        <div
          style={{
            display: 'none',
            gap: '2rem',
            alignItems: 'center',
          }}
          className="desktop-nav"
        >
          {navItems.map((item) => (
            <div
              key={item.label}
              style={{ position: 'relative' }}
              onMouseEnter={() => item.dropdown && setActiveDropdown(item.label)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              <a
                href={item.href}
                onClick={(e) => handleNavClick(item.href, e)}
                style={{
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.base,
                  fontWeight: theme.typography.fontWeight.medium,
                  color: location.pathname === item.href ? theme.colors.primary : theme.colors.dark,
                  textDecoration: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                  transition: `color ${theme.transitions.fast}`,
                  cursor: 'pointer',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.color = theme.colors.primary;
                }}
                onMouseOut={(e) => {
                  if (location.pathname !== item.href) {
                    e.currentTarget.style.color = theme.colors.dark;
                  }
                }}
              >
                {item.label}
                {item.dropdown && <ChevronDown size={16} />}
              </a>

              {/* Dropdown Menu */}
              {item.dropdown && activeDropdown === item.label && (
                <div
                  style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    marginTop: '0.5rem',
                    backgroundColor: theme.colors.white,
                    borderRadius: theme.borderRadius.md,
                    boxShadow: theme.shadows.lg,
                    padding: '0.5rem 0',
                    minWidth: '200px',
                    zIndex: theme.zIndex.dropdown,
                  }}
                >
                  {item.dropdown.map((dropdownItem) => (
                    <a
                      key={dropdownItem.label}
                      href={dropdownItem.href}
                      onClick={(e) => handleNavClick(dropdownItem.href, e)}
                      style={{
                        display: 'block',
                        padding: '0.75rem 1rem',
                        fontFamily: theme.typography.fontBody,
                        fontSize: theme.typography.fontSize.sm,
                        color: theme.colors.dark,
                        textDecoration: 'none',
                        transition: `background-color ${theme.transitions.fast}`,
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.backgroundColor = theme.colors.light;
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                    >
                      {dropdownItem.label}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Mobile Menu Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Mobile Menu Toggle */}
          <button
            style={{
              display: 'none',
              padding: '0.5rem',
              backgroundColor: 'transparent',
              border: 'none',
              color: theme.colors.dark,
              cursor: 'pointer',
            }}
            className="mobile-menu-toggle"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div
          style={{
            display: 'none',
            backgroundColor: theme.colors.white,
            borderTop: `1px solid ${theme.colors.light}`,
            padding: '1rem 1.5rem',
          }}
          className="mobile-menu"
        >
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              onClick={(e) => handleNavClick(item.href, e)}
              style={{
                display: 'block',
                padding: '0.75rem 0',
                fontFamily: theme.typography.fontBody,
                fontSize: theme.typography.fontSize.base,
                fontWeight: theme.typography.fontWeight.medium,
                color: location.pathname === item.href ? theme.colors.primary : theme.colors.dark,
                textDecoration: 'none',
                borderBottom: `1px solid ${theme.colors.light}`,
              }}
            >
              {item.label}
            </a>
          ))}
        </div>
      )}

      {/* Responsive CSS */}
      <style>{`
        @media (min-width: ${theme.breakpoints.md}) {
          .desktop-nav {
            display: flex !important;
          }
        }
        
        @media (max-width: ${theme.breakpoints.md}) {
          .mobile-menu-toggle {
            display: block !important;
          }
          .mobile-menu {
            display: block !important;
          }
        }
      `}</style>
    </header>
  );
};

export default Header;
