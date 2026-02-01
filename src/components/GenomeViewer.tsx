import React, { useMemo, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, PerspectiveCamera } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import { useGenomeStore } from '../store/genome.store';

// Компонент отрисовки ДНК как светящейся трубки
const ChromatinFiber = () => {
  const { cohesins, genomeLength } = useGenomeStore();
  
  // Создаем путь для трубки
  const { path, loopIndices } = useMemo(() => {
    const points: THREE.Vector3[] = [];
    const radius = 20; // Радиус кольца
    const segments = 500; // Детализация основной нити
    
    // 1. Базовое кольцо (Scaffold)
    for (let i = 0; i <= segments; i++) {
      const theta = (i / segments) * Math.PI * 2;
      points.push(new THREE.Vector3(
        Math.cos(theta) * radius,
        Math.sin(theta) * radius,
        0
      ));
    }

    // 2. Модифицируем точки там, где есть петли (Cohesins)
    // Очень упрощенная визуализация: вытягиваем дуги
    // В реальном проекте здесь нужно брать координаты из engine.getVisCoordinates()
    // Но для красоты пока сделаем процедурную деформацию на основе данных стора
    
    const curvePath = new THREE.CatmullRomCurve3(points);
    curvePath.closed = true;
    
    return { path: curvePath, loopIndices: [] };
  }, [genomeLength]); // Пересчитываем только если длина меняется (для оптимизации)

  // А вот здесь рисуем АКТИВНЫЕ петли динамически
  const loopsGeometry = useMemo(() => {
    if (cohesins.length === 0) return null;

    const curves: THREE.CatmullRomCurve3[] = [];
    const radius = 20;

    cohesins.forEach(lef => {
        // Нормализуем координаты [0, 1]
        const startNorm = lef.left / genomeLength;
        const endNorm = lef.right / genomeLength;
        
        // Угол на круге
        const startTheta = startNorm * Math.PI * 2;
        const endTheta = endNorm * Math.PI * 2;

        // Вычисляем середину петли
        let midTheta = (startTheta + endTheta) / 2;
        if (endTheta < startTheta) midTheta += Math.PI; // Обработка перехода через 0

        // Высота петли зависит от её размера
        const loopSize = Math.abs(lef.right - lef.left);
        const extrusionHeight = Math.min(loopSize / 2000, 15); // Масштабирование высоты

        // Строим 3 точки для кривой Безье (Start -> Mid -> End)
        const p1 = new THREE.Vector3(Math.cos(startTheta)*radius, Math.sin(startTheta)*radius, 0);
        const p2 = new THREE.Vector3(Math.cos(midTheta)*(radius + extrusionHeight), Math.sin(midTheta)*(radius + extrusionHeight), extrusionHeight * 0.5); // Немного в 3D (Z)
        const p3 = new THREE.Vector3(Math.cos(endTheta)*radius, Math.sin(endTheta)*radius, 0);

        curves.push(new THREE.CatmullRomCurve3([p1, p2, p3]));
    });

    return curves;
  }, [cohesins, genomeLength]);

  return (
    <group>
      {/* Основное кольцо хроматина (темное) */}
      <mesh>
        <tubeGeometry args={[path, 200, 0.1, 8, true]} />
        <meshStandardMaterial 
            color="#2a0a4d" 
            emissive="#1a0530"
            roughness={0.4}
            metalness={0.8}
        />
      </mesh>

      {/* Активные петли (светящиеся) */}
      {loopsGeometry && loopsGeometry.map((curve, idx) => (
        <mesh key={idx}>
            <tubeGeometry args={[curve, 20, 0.15, 8, false]} />
            <meshStandardMaterial 
                color="#00ffff" 
                emissive="#00ffff"
                emissiveIntensity={2}
                toneMapped={false} // Важно для Bloom эффекта
            />
        </mesh>
      ))}
    </group>
  );
};

const SceneContent = () => {
    const groupRef = useRef<THREE.Group>(null);
    
    // Медленное вращение всей сцены
    useFrame((state, delta) => {
        if (groupRef.current) {
            groupRef.current.rotation.z += delta * 0.05;
        }
    });

    return (
        <group ref={groupRef}>
            <ChromatinFiber />
        </group>
    );
};

export const GenomeViewer: React.FC = () => {
  return (
    <div className="w-full h-full bg-black rounded-lg overflow-hidden shadow-2xl border border-gray-800">
      <Canvas dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 0, 60]} fov={50} />
        
        {/* Освещение */}
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight position={[-10, -10, -10]} angle={0.3} intensity={2} color="#ff00cc" />

        {/* Контент сцены */}
        <SceneContent />
        
        {/* Красивый фон */}
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

        {/* Пост-процессинг для свечения */}
        <EffectComposer disableNormalPass>
            <Bloom 
                luminanceThreshold={0.2} // Светятся только яркие объекты
                mipmapBlur // Мягкое размытие
                intensity={1.5} // Сила свечения
                radius={0.8}
            />
            <Vignette eskil={false} offset={0.1} darkness={1.1} />
        </EffectComposer>

        <OrbitControls 
            enablePan={true} 
            enableZoom={true} 
            minDistance={10} 
            maxDistance={200}
            autoRotate={false}
        />
      </Canvas>
      
      <div className="absolute bottom-4 left-4 text-xs text-gray-500 font-mono pointer-events-none">
        RENDERER: WebGL2 + Bloom
        <br/>
        VISUALIZATION: Volumetric Tube
      </div>
    </div>
  );
};
