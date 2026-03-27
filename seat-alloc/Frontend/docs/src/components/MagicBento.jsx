import React, { useRef, useEffect } from 'react';
import gsap from 'gsap';

const MagicBento = ({
    children,
    className = "",
    textAutoHide = false,
    enableStars = true,
    enableSpotlight = true,
    enableBorderGlow = true,
    enableTilt = true,
    enableMagnetism = true,
    clickEffect = true,
    spotlightRadius = 300,
    particleCount = 12, // Reduced for performance in multiple cards
    glowColor = "132, 0, 255" // Defaults to purple-ish
}) => {
    const containerRef = useRef(null);
    const glowRef = useRef(null);
    const canvasRef = useRef(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        // --- Spotlight Effect ---
        if (enableSpotlight) {
            const handleMouseMove = (e) => {
                const rect = container.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                if (glowRef.current) {
                    gsap.to(glowRef.current, {
                        x: x,
                        y: y,
                        duration: 0.1, // Faster follow
                        ease: "power2.out",
                        opacity: 1
                    });
                }
            };

            const handleMouseLeave = () => {
                if (glowRef.current) {
                    gsap.to(glowRef.current, {
                        opacity: 0,
                        duration: 0.5
                    });
                }
            };

            container.addEventListener('mousemove', handleMouseMove);
            container.addEventListener('mouseleave', handleMouseLeave);

            return () => {
                container.removeEventListener('mousemove', handleMouseMove);
                container.removeEventListener('mouseleave', handleMouseLeave);
            }
        }
    }, [enableSpotlight]);


    // --- Stars Effect (Canvas) ---
    useEffect(() => {
        if (!enableStars || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const container = containerRef.current;
        let animationFrameId;
        let particles = [];

        const resizeCanvas = () => {
            if (container) {
                canvas.width = container.offsetWidth;
                canvas.height = container.offsetHeight;
            }
        };

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.2;
                this.vy = (Math.random() - 0.5) * 0.2;
                this.size = Math.random() * 1.5;
                this.alpha = Math.random() * 0.8;
                this.glowing = Math.random() > 0.5;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                // Bounce off edges
                if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

                // Twinkle
                if (this.glowing) {
                    this.alpha += (Math.random() - 0.5) * 0.05;
                    if (this.alpha < 0.2) this.alpha = 0.2;
                    if (this.alpha > 0.8) this.alpha = 0.8;
                }
            }

            draw() {
                ctx.fillStyle = `rgba(255, 255, 255, ${this.alpha})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        const initParticles = () => {
            particles = [];
            for (let i = 0; i < particleCount; i++) {
                particles.push(new Particle());
            }
        };

        const animate = () => {
            if (!ctx) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            animationFrameId = requestAnimationFrame(animate);
        };

        resizeCanvas();
        initParticles();
        animate();

        window.addEventListener('resize', resizeCanvas);

        return () => {
            cancelAnimationFrame(animationFrameId);
            window.removeEventListener('resize', resizeCanvas);
        };
    }, [enableStars, particleCount]);



    return (
        <div
            ref={containerRef}
            className={`magic-bento-card ${className}`}
            style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                backgroundColor: 'transparent',
                borderRadius: '12px',
                border: '1px solid rgba(255,255,255,0)', // Invisible by default
                transition: 'all 0.3s ease',
                cursor: clickEffect ? 'pointer' : 'default',
                padding: '20px',
                height: '100%'
            }}
            onMouseEnter={(e) => {
                // Reveal background and border on hover
                gsap.to(e.currentTarget, {
                    backgroundColor: 'var(--ifm-card-background-color)',
                    borderColor: enableBorderGlow ? 'rgba(255,255,255,0.1)' : 'transparent',
                    duration: 0.3
                });
                if (enableTilt) gsap.to(e.currentTarget, { scale: 1.02, duration: 0.3, boxShadow: '0 10px 30px -10px rgba(0,0,0,0.5)' });
            }}
            onMouseLeave={(e) => {
                // Hide background and border on leave
                gsap.to(e.currentTarget, {
                    backgroundColor: 'transparent',
                    borderColor: 'rgba(255,255,255,0)',
                    duration: 0.3
                });
                if (enableTilt) gsap.to(e.currentTarget, { scale: 1, duration: 0.3, boxShadow: 'none' });
            }}
        >
            {/* Glow Element */}
            {enableSpotlight && (
                <div
                    ref={glowRef}
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '0px',
                        height: '0px',
                        borderRadius: '50%',
                        background: `radial-gradient(circle closest-side, rgba(${glowColor}, 0.2), transparent)`,
                        boxShadow: `0 0 ${spotlightRadius}px ${spotlightRadius / 2}px rgba(${glowColor}, 0.2)`,
                        pointerEvents: 'none',
                        opacity: 0, // Hidden by default
                        zIndex: 1,
                        transform: 'translate(-50%, -50%)' // Center on mouse
                    }}
                />
            )}

            {/* Stars Canvas */}
            {enableStars && (
                <canvas
                    ref={canvasRef}
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        pointerEvents: 'none',
                        zIndex: 0
                    }}
                />
            )}

            {/* Content */}
            <div style={{ position: 'relative', zIndex: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
                {children}
            </div>
        </div>
    );
};

export default MagicBento;
