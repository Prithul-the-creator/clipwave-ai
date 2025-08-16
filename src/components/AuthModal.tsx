import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Auth } from "@supabase/auth-ui-react";
import { ThemeSupa } from "@supabase/auth-ui-shared";
import { supabase } from "@/integrations/supabase/client";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (email: string) => void;
}

export const AuthModal = ({ isOpen, onClose, onLogin }: AuthModalProps) => {
  useEffect(() => {
    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === 'SIGNED_IN' && session?.user) {
          onLogin(session.user.email || '');
          onClose();
        }
      }
    );

    return () => subscription.unsubscribe();
  }, [onLogin, onClose]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md glass-effect border-0 shadow-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl text-center glow-text bg-gradient-to-r from-neon-blue to-neon-purple bg-clip-text text-transparent">
            Welcome to ClipWave
          </DialogTitle>
        </DialogHeader>
        
        <Auth
          supabaseClient={supabase}
          appearance={{ 
            theme: ThemeSupa,
            variables: {
              default: {
                colors: {
                  brand: '#3b82f6',
                  brandAccent: '#8b5cf6',
                  brandButtonText: '#ffffff',
                  defaultButtonBackground: '#1e293b',
                  defaultButtonBackgroundHover: '#334155',
                  defaultButtonBorder: '#475569',
                  defaultButtonText: '#ffffff',
                  dividerBackground: '#475569',
                  inputBackground: '#1e293b',
                  inputBorder: '#475569',
                  inputBorderHover: '#3b82f6',
                  inputBorderFocus: '#8b5cf6',
                  inputText: '#ffffff',
                  inputLabelText: '#94a3b8',
                  inputPlaceholder: '#64748b',
                  messageText: '#ffffff',
                  messageTextDanger: '#ef4444',
                  anchorTextColor: '#3b82f6',
                  anchorTextHoverColor: '#8b5cf6',
                },
                borderWidths: {
                  buttonBorderWidth: '1px',
                  inputBorderWidth: '1px',
                },
                fontSizes: {
                  baseBodySize: '14px',
                  baseInputSize: '14px',
                  baseLabelSize: '14px',
                  baseButtonSize: '14px',
                },
                fonts: {
                  bodyFontFamily: 'Inter, system-ui, sans-serif',
                  buttonFontFamily: 'Inter, system-ui, sans-serif',
                  inputFontFamily: 'Inter, system-ui, sans-serif',
                  labelFontFamily: 'Inter, system-ui, sans-serif',
                },
                radii: {
                  borderRadiusButton: '8px',
                  buttonBorderRadius: '8px',
                  inputBorderRadius: '8px',
                },
                space: {
                  inputPadding: '12px',
                  buttonPadding: '12px 24px',
                }
              }
            },
            className: {
              anchor: 'text-neon-blue hover:text-neon-purple transition-colors',
              button: 'bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-purple hover:to-neon-pink text-white font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-neon-blue/25',
              container: 'glass-effect',
              divider: 'bg-dark-card',
              input: 'bg-dark-card/50 border-neon-blue/30 focus:border-neon-blue text-white placeholder:text-muted-foreground',
              label: 'text-white font-medium',
              loader: 'text-neon-blue',
              message: 'text-white',
            }
          }}
          providers={["google"]}
          redirectTo={window.location.origin}
        />
      </DialogContent>
    </Dialog>
  );
};
