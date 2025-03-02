import React, { useEffect, useState } from 'react';
import { Bomb, Skull, Shield, Terminal, AlertTriangle, Zap, Flame, Bug, Brush as Virus, Radiation, Sparkles, CloudLightning as Lightning, Siren } from 'lucide-react';

function FlyingText() {
  const [position, setPosition] = useState({
    top: Math.random() * 100,
    left: -20,
    size: 16 + Math.random() * 24,
    speed: 2 + Math.random() * 5,
    color: `hsl(${Math.random() * 60}, 100%, 50%)`,
    rotation: Math.random() * 30 - 15
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setPosition(prev => ({
        ...prev,
        left: prev.left + prev.speed,
        top: prev.top + (Math.random() * 2 - 1),
        rotation: prev.rotation + (Math.random() * 4 - 2)
      }));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  if (position.left > 120) {
    // Reset position when it goes off screen
    setPosition({
      top: Math.random() * 100,
      left: -20,
      size: 16 + Math.random() * 24,
      speed: 2 + Math.random() * 5,
      color: `hsl(${Math.random() * 60}, 100%, 50%)`,
      rotation: Math.random() * 30 - 15
    });
  }

  return (
    <div 
      className="fixed font-bold font-mono whitespace-nowrap"
      style={{
        top: `${position.top}%`,
        left: `${position.left}%`,
        fontSize: `${position.size}px`,
        color: position.color,
        textShadow: '2px 2px 4px rgba(0,0,0,0.7)',
        transform: `rotate(${position.rotation}deg)`,
        zIndex: 20,
      }}
    >
      GIGABLASTED!!!
    </div>
  );
}

function FloatingIcon({ Icon }) {
  const [position, setPosition] = useState({
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: 16 + Math.random() * 32,
    speed: {
      x: (Math.random() - 0.5) * 2,
      y: (Math.random() - 0.5) * 2
    },
    rotation: Math.random() * 360,
    rotationSpeed: (Math.random() - 0.5) * 5,
    color: `hsl(${Math.random() * 360}, 100%, 50%)`
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setPosition(prev => {
        let newX = prev.x + prev.speed.x;
        let newY = prev.y + prev.speed.y;
        
        // Bounce off edges
        if (newX < 0 || newX > 100) prev.speed.x *= -1;
        if (newY < 0 || newY > 100) prev.speed.y *= -1;
        
        return {
          ...prev,
          x: Math.max(0, Math.min(100, newX)),
          y: Math.max(0, Math.min(100, newY)),
          rotation: (prev.rotation + prev.rotationSpeed) % 360
        };
      });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <div 
      className="absolute"
      style={{
        top: `${position.y}%`,
        left: `${position.x}%`,
        transform: `rotate(${position.rotation}deg)`,
        transition: 'transform 0.5s ease',
        zIndex: 5,
      }}
    >
      <Icon 
        size={position.size} 
        style={{ color: position.color }} 
        className="drop-shadow-lg" 
      />
    </div>
  );
}

function App() {
  const [flyingTexts, setFlyingTexts] = useState([]);
  const [glitchEffect, setGlitchEffect] = useState(false);
  
  const icons = [Bomb, Skull, Shield, Terminal, AlertTriangle, Zap, Flame, Bug, Virus, Radiation, Sparkles, Lightning];

  useEffect(() => {
    // Create new flying texts at random intervals
    const createInterval = setInterval(() => {
      setFlyingTexts(prev => [...prev, Date.now()]);
    }, 800);

    // Clean up old flying texts to prevent too many elements
    const cleanupInterval = setInterval(() => {
      setFlyingTexts(prev => {
        if (prev.length > 15) {
          return prev.slice(prev.length - 15);
        }
        return prev;
      });
    }, 5000);
    
    // Random glitch effect
    const glitchInterval = setInterval(() => {
      setGlitchEffect(true);
      setTimeout(() => setGlitchEffect(false), 200);
    }, 3000);

    return () => {
      clearInterval(createInterval);
      clearInterval(cleanupInterval);
      clearInterval(glitchInterval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-red-900 flex flex-col items-center justify-center text-center p-4 overflow-hidden relative">
      {/* Glitch overlay */}
      {glitchEffect && (
        <div className="fixed inset-0 bg-green-500 mix-blend-screen opacity-30 z-50"></div>
      )}
      
      {/* Flying GIGABLASTED texts */}
      {flyingTexts.map(id => (
        <FlyingText key={id} />
      ))}
      
      {/* Background animated elements */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(30)].map((_, i) => (
          <div 
            key={i}
            className="absolute animate-ping opacity-30"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDuration: `${1 + Math.random() * 3}s`,
              animationDelay: `${Math.random() * 2}s`
            }}
          >
            <Zap className="text-yellow-400 h-8 w-8" />
          </div>
        ))}
      </div>
      
      {/* Floating icons */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <FloatingIcon key={i} Icon={icons[i % icons.length]} />
        ))}
      </div>
      
      {/* Animated background gradient */}
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          background: 'linear-gradient(45deg, #ff0000, #ff7700, #ffff00, #ff0000)',
          backgroundSize: '400% 400%',
          animation: 'gradient 15s ease infinite',
        }}
      ></div>
      
      <style jsx>{`
        @keyframes gradient {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
      `}</style>
      
      <div className="max-w-3xl w-full bg-black rounded-lg shadow-2xl overflow-hidden border-4 border-yellow-400 animate-pulse relative z-10">
        <div className="bg-yellow-400 p-3 flex items-center justify-center space-x-2">
          <AlertTriangle className="text-red-900 h-6 w-6 animate-bounce" />
          <h2 className="text-xl font-mono font-bold text-red-900 animate-pulse">GIGABLASTING!!!!!!!</h2>
          <AlertTriangle className="text-red-900 h-6 w-6 animate-bounce" />
        </div>
        
        <div className="p-6 text-white">
          <div className="flex justify-center mb-4">
            <Terminal className="h-16 w-16 text-green-500 animate-spin" style={{ animationDuration: '3s' }} />
          </div>
          
          <h1 className="text-5xl font-bold mb-6 text-yellow-400 animate-bounce">
            YOU'VE BEEN GIGABLASTED!
          </h1>
          
          <div className="mb-8 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-red-500 via-yellow-500 to-red-500 animate-pulse opacity-50 rounded-lg"></div>
            <img 
              src="https://ist.psu.edu/sites/default/files/directory/Giacobe-Nicklaus.png" 
              alt="Professor Nicklaus Giacobe" 
              className="rounded-lg mx-auto border-2 border-yellow-400 shadow-lg relative z-10"
            />
          </div>
          
          <div className="flex justify-center space-x-4 mb-6">
            <Bomb className="h-8 w-8 text-red-500 animate-bounce" style={{ animationDuration: '0.8s' }} />
            <Skull className="h-8 w-8 text-white animate-pulse" style={{ animationDuration: '1.2s' }} />
            <Shield className="h-8 w-8 text-green-500 animate-spin" style={{ animationDuration: '2s' }} />
            <Flame className="h-8 w-8 text-orange-500 animate-bounce" style={{ animationDuration: '0.7s' }} />
          </div>
          
          <p className="text-green-400 font-mono text-lg mb-4 animate-pulse">
            I JUST GIGABLASTED ALL OVER THE PLACE!
          </p>
          
          <div className="flex flex-wrap justify-center gap-3 my-6">
            {['HACKED', 'PWNED', 'OWNED', 'GIGABLASTED', 'BOOM!'].map((text, i) => (
              <div 
                key={i} 
                className="bg-red-600 text-white px-3 py-1 rounded-full font-bold animate-bounce"
                style={{ animationDelay: `${i * 0.2}s` }}
              >
                {text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;