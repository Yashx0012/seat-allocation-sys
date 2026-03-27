// src/components/LensCard.jsx
import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';

const LensCard = ({ children, className = '', lensSize = 150, zoomFactor = 1.5 }) => {
  const containerRef = useRef(null);
  const [isHovering, setIsHovering] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [lensPosition, setLensPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Clamp lens position within bounds
    const lensX = Math.max(0, Math.min(x - lensSize / 2, rect.width - lensSize));
    const lensY = Math.max(0, Math.min(y - lensSize / 2, rect.height - lensSize));

    setMousePosition({ x, y });
    setLensPosition({ x: lensX, y: lensY });
  };

  const handleMouseEnter = () => setIsHovering(true);
  const handleMouseLeave = () => setIsHovering(false);

  return (
    <div
      ref={containerRef}
      className={`relative overflow-hidden ${className}`}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Original content */}
      {children}

      {/* Lens effect overlay */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{
          opacity: isHovering ? 1 : 0,
          scale: isHovering ? 1 : 0.8,
          x: lensPosition.x,
          y: lensPosition.y,
        }}
        transition={{ duration: 0.15, ease: 'easeOut' }}
        className="pointer-events-none absolute rounded-full border-2 border-white/30 shadow-2xl overflow-hidden backdrop-blur-[1px]"
        style={{
          width: lensSize,
          height: lensSize,
          top: 0,
          left: 0,
        }}
      >
        {/* Magnified content */}
        <div
          className="absolute"
          style={{
            width: containerRef.current?.offsetWidth || 0,
            height: containerRef.current?.offsetHeight || 0,
            transform: `scale(${zoomFactor})`,
            transformOrigin: `${mousePosition.x}px ${mousePosition.y}px`,
            left: -lensPosition.x,
            top: -lensPosition.y,
          }}
        >
          {children}
        </div>

        {/* Lens glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent rounded-full" />
        <div className="absolute inset-0 ring-1 ring-inset ring-white/20 rounded-full" />
      </motion.div>
    </div>
  );
};

export default LensCard;