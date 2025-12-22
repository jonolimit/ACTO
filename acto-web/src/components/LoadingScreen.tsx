import { useState, useEffect } from 'react';

interface LoadingScreenProps {
  imagesToPreload?: string[];
  minLoadTime?: number;
  maxLoadTime?: number;
}

export function LoadingScreen({
  imagesToPreload = ['/hero.png'],
  minLoadTime = 300,
  maxLoadTime = 3000,
}: LoadingScreenProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    let imagesLoaded = 0;
    let minTimeElapsed = false;
    let loadingComplete = false;

    const checkComplete = () => {
      if (loadingComplete) return;

      const allImagesLoaded = imagesLoaded >= imagesToPreload.length;
      
      if (allImagesLoaded && minTimeElapsed) {
        loadingComplete = true;
        setIsLoading(false);
        // Wait for fade out animation before removing from DOM
        setTimeout(() => setIsVisible(false), 400);
      }
    };

    // Minimum load time for smooth UX
    setTimeout(() => {
      minTimeElapsed = true;
      checkComplete();
    }, minLoadTime);

    // Preload images
    imagesToPreload.forEach((src) => {
      const img = new Image();
      img.src = src;

      const handleLoad = () => {
        imagesLoaded++;
        checkComplete();
      };

      img.onload = handleLoad;
      img.onerror = handleLoad; // Continue even if image fails

      // Handle already cached images
      if (img.complete) {
        handleLoad();
      }
    });

    // Fallback: max load time
    const fallbackTimer = setTimeout(() => {
      if (!loadingComplete) {
        loadingComplete = true;
        setIsLoading(false);
        setTimeout(() => setIsVisible(false), 400);
      }
    }, maxLoadTime);

    return () => clearTimeout(fallbackTimer);
  }, [imagesToPreload, minLoadTime, maxLoadTime]);

  if (!isVisible) return null;

  return (
    <div className={`loading-screen ${!isLoading ? 'loading-screen--hidden' : ''}`}>
      <img src="/logo_w.png" alt="ACTO" className="loading-logo" />
      <div className="loading-spinner" />
      <div className="loading-text">Loading...</div>
    </div>
  );
}

