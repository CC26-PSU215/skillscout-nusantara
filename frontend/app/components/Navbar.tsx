"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Search,
  Upload,
  Briefcase,
  TrendingUp,
  Menu,
  X,
  Zap,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/",        label: "Beranda",  icon: Zap },
  { href: "/upload",  label: "Upload CV", icon: Upload },
  { href: "/jobs",    label: "Lowongan",  icon: Briefcase },
  { href: "/trends",  label: "Tren Skill", icon: TrendingUp },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        background: "rgba(11, 15, 26, 0.85)",
        backdropFilter: "blur(16px)",
        WebkitBackdropFilter: "blur(16px)",
        borderBottom: "1px solid var(--glass-border)",
      }}
    >
      <div
        className="page-container"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          height: 64,
        }}
      >
        {/* Logo */}
        <Link
          href="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            fontWeight: 800,
            fontSize: "1.125rem",
          }}
        >
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: 32,
              height: 32,
              borderRadius: "var(--radius-sm)",
              background: "var(--gradient-primary)",
            }}
          >
            <Search size={16} color="#fff" />
          </span>
          <span>
            Skill<span style={{ color: "var(--primary-400)" }}>Scout</span>
          </span>
        </Link>

        {/* Desktop nav */}
        <ul
          style={{
            display: "flex",
            gap: 4,
            listStyle: "none",
            alignItems: "center",
          }}
          className="desktop-nav"
        >
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "8px 16px",
                    borderRadius: "var(--radius-md)",
                    fontSize: "0.875rem",
                    fontWeight: active ? 600 : 400,
                    color: active
                      ? "var(--primary-300)"
                      : "var(--text-secondary)",
                    background: active
                      ? "rgba(99, 102, 241, 0.1)"
                      : "transparent",
                    transition: "var(--transition-fast)",
                  }}
                >
                  <Icon size={16} />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* Mobile toggle */}
        <button
          className="mobile-toggle"
          onClick={() => setMobileOpen(!mobileOpen)}
          style={{
            display: "none",
            background: "none",
            border: "none",
            color: "var(--text-primary)",
            cursor: "pointer",
            padding: 8,
          }}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div
          className="mobile-menu"
          style={{
            padding: "16px 24px",
            borderTop: "1px solid var(--glass-border)",
            background: "rgba(11, 15, 26, 0.95)",
          }}
        >
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "12px 16px",
                  borderRadius: "var(--radius-md)",
                  fontSize: "0.9375rem",
                  fontWeight: active ? 600 : 400,
                  color: active
                    ? "var(--primary-300)"
                    : "var(--text-secondary)",
                  background: active
                    ? "rgba(99, 102, 241, 0.1)"
                    : "transparent",
                  marginBottom: 4,
                }}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </div>
      )}

      <style jsx global>{`
        @media (max-width: 768px) {
          .desktop-nav {
            display: none !important;
          }
          .mobile-toggle {
            display: block !important;
          }
        }
        @media (min-width: 769px) {
          .mobile-menu {
            display: none !important;
          }
        }
      `}</style>
    </nav>
  );
}
