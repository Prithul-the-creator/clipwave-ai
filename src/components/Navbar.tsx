import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { User, Settings, LogOut, Zap } from 'lucide-react';

interface NavbarProps {
  user: { email: string; name?: string } | null;
  onLogin: () => void;
  onLogout: () => void;
}

const NAV_LINKS = [
  { label: 'About', href: '#about' },
  { label: 'Features', href: '#features' },
  { label: 'Demo', href: '#demo' },
];

export const Navbar = ({ user, onLogin, onLogout }: NavbarProps) => {
  const [active, setActive] = useState<string>('');

  useEffect(() => {
    const handleScroll = () => {
      let found = '';
      for (const link of NAV_LINKS) {
        const section = document.querySelector(link.href);
        if (section) {
          const rect = (section as HTMLElement).getBoundingClientRect();
          if (rect.top <= 80 && rect.bottom > 80) {
            found = link.href;
            break;
          }
        }
      }
      setActive(found);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className="fixed top-6 left-1/2 z-50 -translate-x-1/2 w-[95vw] max-w-5xl flex items-center justify-between px-4 py-2 bg-white/90 shadow-xl rounded-full border border-gray-200 backdrop-blur-lg animate-fade-in">
      {/* Left: Logo + Beta */}
      <div className="flex items-center gap-3 pl-2">
        <div className="p-2 bg-black rounded-full shadow">
          <Zap className="h-6 w-6 text-white" />
        </div>
        <a
          href="/#about"
          className="font-bold text-xl text-gray-900 select-none hover:underline focus:outline-none"
          onClick={e => {
            if (user) {
              e.preventDefault();
              onLogout();
              setTimeout(() => {
                window.location.href = '/#about';
              }, 100);
            }
          }}
        >
          ClipWaveAI
        </a>
        <span className="ml-2 px-2 py-0.5 bg-pink-100 text-pink-600 text-xs rounded-full font-semibold tracking-wide">Beta</span>
      </div>
      {/* Center: Nav Links */}
      <div className="flex gap-8">
        {NAV_LINKS.map((link) => (
          <a
            key={link.label}
            href={link.href}
            className={`relative font-semibold text-gray-800 px-2 py-1 transition group ${active === link.href ? 'text-blue-600' : 'hover:text-blue-500'}`}
            style={{ transition: 'color 0.2s' }}
          >
            {link.label}
            <span
              className={`absolute left-0 -bottom-1 h-0.5 rounded-full bg-blue-500 transition-all duration-300 ${active === link.href ? 'w-full opacity-100' : 'w-0 opacity-0'} group-hover:w-full group-hover:opacity-60`}
            />
          </a>
        ))}
      </div>
      {/* Right: User Dropdown or Sign In */}
      <div className="pr-2">
        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar className="h-10 w-10">
                  <AvatarImage src="" alt={user.name || user.email} />
                  <AvatarFallback className="bg-blue-100 text-blue-600">
                    {user.name ? user.name[0].toUpperCase() : user.email[0].toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 border-0 shadow-2xl rounded-xl" align="end">
              <div className="flex items-center justify-start gap-2 p-2">
                <div className="flex flex-col space-y-1 leading-none">
                  {user.name && (
                    <p className="font-medium text-gray-900">{user.name}</p>
                  )}
                  <p className="w-[200px] truncate text-sm text-gray-500">
                    {user.email}
                  </p>
                </div>
              </div>
              <DropdownMenuSeparator className="bg-gray-200" />
              <DropdownMenuItem className="hover:bg-gray-100 cursor-pointer">
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem className="hover:bg-gray-100 cursor-pointer">
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-200" />
              <DropdownMenuItem 
                onClick={onLogout}
                className="hover:bg-red-100 hover:text-red-600 cursor-pointer"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Button 
            onClick={onLogin}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-full transition-all duration-300 shadow"
          >
            Sign In
          </Button>
        )}
      </div>
    </nav>
  );
};

export default Navbar; 