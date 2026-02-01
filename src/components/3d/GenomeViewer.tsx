import React, { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import * as THREE from 'three';
import { LoopExtrusionEngine } from '../../engines/LoopExtrusionEngine';
import { CTCFSite, Loop } from '../../domain/models/genome';

interface GenomeViewerProps {
    engine?: LoopExtrusionEngine;
    genomeLength?: number;
    loops?: Loop[];
    ctcfSites?: CTCFSite[];
}

const ChromatinTube = ({ genomeLength, loops, ctcfSites }: { genomeLength: number; loops: Loop[]; ctcfSites: CTCFSite[] }) => {
    const mainPath = useMemo(() => {
        const points: THREE.Vector3[] = [];
        const radius = 25;
        for (let i = 0; i <= 100; i++) {
            const theta = (i / 100) * Math.PI * 2;
            points.push(new THREE.Vector3(Math.cos(theta) * radius, Math.sin(theta) * radius, 0));
        }
        return new THREE.CatmullRomCurve3(points, true);
    }, []);

    const loopCurves = useMemo(() => {
        return loops.map(loop => {
            const radius = 25;
            const startAngle = (loop.leftAnchor / genomeLength) * Math.PI * 2;
            const endAngle = (loop.rightAnchor / genomeLength) * Math.PI * 2;
            let midAngle = (startAngle + endAngle) / 2;
            if (endAngle < startAngle) midAngle += Math.PI;
            const height = 15;
            const p1 = new THREE.Vector3(Math.cos(startAngle) * radius, Math.sin(startAngle) * radius, 0);
            const p2 = new THREE.Vector3(Math.cos(midAngle) * (radius + height), Math.sin(midAngle) * (radius + height), 5);
            const p3 = new THREE.Vector3(Math.cos(endAngle) * radius, Math.sin(endAngle) * radius, 0);
            return new THREE.CatmullRomCurve3([p1, p2, p3]);
        });
    }, [loops, genomeLength]);

    return (
        <group>
            <mesh>
                <tubeGeometry args={[mainPath, 200, 0.8, 12, true]} />
                <meshStandardMaterial color="#6600cc" emissive="#220044" emissiveIntensity={0.8} roughness={0.3} metalness={0.8} />
            </mesh>
            {loopCurves.map((curve, i) => (
                <mesh key={i}>
                    <tubeGeometry args={[curve, 32, 0.5, 12, false]} />
                    <meshStandardMaterial color="#00ffff" emissive="#00ffff" emissiveIntensity={3} roughness={0.1} metalness={0.9} />
                </mesh>
            ))}
        </group>
    );
};

export const GenomeViewer: React.FC<GenomeViewerProps> = ({ engine }) => {
    const data = useMemo(() => {
        if (engine) {
            return { genomeLength: engine.genomeLength, loops: engine.getLoops(), ctcfSites: engine.ctcfSites };
        }
        return { genomeLength: 100000, loops: [] as Loop[], ctcfSites: [] as CTCFSite[] };
    }, [engine]);

    return (
        <div className="w-full h-full bg-black relative">
            <Canvas camera={{ position: [0, 0, 80], fov: 45 }} gl={{ antialias: true }}>
                <color attach="background" args={['#050510']} />
                <ambientLight intensity={0.6} />
                <pointLight position={[20, 20, 20]} intensity={1.5} />
                <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={0.5} />
                <ChromatinTube genomeLength={data.genomeLength} loops={data.loops} ctcfSites={data.ctcfSites} />
                <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
            </Canvas>
            <div className="absolute bottom-4 left-4 text-white text-xs font-mono">MODE: NEON TUBE v2.0</div>
        </div>
    );
};

export default GenomeViewer;
