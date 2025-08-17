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
      <DialogContent className="sm:max-w-md bg-gradient-to-br from-gray-900/95 to-black/95 backdrop-blur-xl border border-white/10 shadow-2xl">
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
                  defaultButtonBackground: 'transparent',
                  defaultButtonBackgroundHover: 'rgba(59, 130, 246, 0.1)',
                  defaultButtonBorder: 'rgba(59, 130, 246, 0.3)',
                  defaultButtonText: '#ffffff',
                  dividerBackground: 'rgba(255, 255, 255, 0.1)',
                  inputBackground: 'transparent',
                  inputBorder: 'rgba(255, 255, 255, 0.2)',
                  inputBorderHover: 'rgba(59, 130, 246, 0.5)',
                  inputBorderFocus: 'rgba(139, 92, 246, 0.8)',
                  inputText: '#ffffff',
                  inputLabelText: '#ffffff',
                  inputPlaceholder: 'rgba(255, 255, 255, 0.6)',
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
              container: '!bg-transparent !border-0 !shadow-none',
              divider: 'bg-white/10',
              input: '!bg-transparent !border-white/20 focus:!border-neon-blue/50 text-white placeholder:text-white/60 backdrop-blur-sm',
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
