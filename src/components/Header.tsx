import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { User, Settings, LogOut, Zap } from 'lucide-react';

interface HeaderProps {
  user: { email: string; name?: string } | null;
  onLogin: () => void;
  onLogout: () => void;
}

export const Header = ({ user, onLogin, onLogout }: HeaderProps) => {
  return (
    <header className="bg-gradient-to-r from-neon-blue/30 to-neon-purple/30 backdrop-blur-md shadow-lg border-b border-white/10 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-neon-blue to-neon-purple rounded-lg shadow">
              <Zap className="h-6 w-6 text-white animate-pulse" />
            </div>
            <span className="font-bold text-2xl text-neon-blue bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent select-none">
              ClipWave
            </span>
            <span className="ml-2 px-2 py-0.5 bg-neon-pink/20 text-neon-pink text-xs rounded-full font-semibold tracking-wide animate-pulse">Beta</span>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex gap-8 relative">
            {[
              { label: 'Features', href: '#features', color: 'neon-blue' },
              { label: 'Pricing', href: '#pricing', color: 'neon-purple' },
              { label: 'About', href: '#about', color: 'neon-pink' },
            ].map((link) => (
              <a
                key={link.label}
                href={link.href}
                className={`relative group text-white font-medium transition`}
              >
                {link.label}
                <span
                  className={`absolute left-0 -bottom-1 h-0.5 w-0 bg-${link.color} transition-all duration-300 group-hover:w-full`}
                />
              </a>
            ))}
          </nav>

          {/* User Menu or Sign In */}
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src="" alt={user.name || user.email} />
                    <AvatarFallback className="bg-neon-blue/20 text-neon-blue">
                      {user.name ? user.name[0].toUpperCase() : user.email[0].toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56 glass-effect border-0 shadow-2xl" align="end">
                <div className="flex items-center justify-start gap-2 p-2">
                  <div className="flex flex-col space-y-1 leading-none">
                    {user.name && (
                      <p className="font-medium text-foreground">{user.name}</p>
                    )}
                    <p className="w-[200px] truncate text-sm text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </div>
                <DropdownMenuSeparator className="bg-dark-surface" />
                <DropdownMenuItem className="hover:bg-dark-card/50 cursor-pointer">
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="hover:bg-dark-card/50 cursor-pointer">
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-dark-surface" />
                <DropdownMenuItem 
                  onClick={onLogout}
                  className="hover:bg-red-500/10 hover:text-red-400 cursor-pointer"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button 
              onClick={onLogin}
              className="bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-purple hover:to-neon-pink text-white font-semibold px-6 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-neon-blue/25"
            >
              Sign In
            </Button>
          )}
        </div>
      </div>
    </header>
  );
};
