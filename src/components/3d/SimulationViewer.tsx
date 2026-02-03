import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { LoopExtrusionEngine } from '../../engines/LoopExtrusionEngine';
import { CTCFSite, Loop } from '../../domain/models/genome';
import { VISUALIZATION_CONFIG } from '../../domain/constants/biophysics';

const DNA_LENGTH = VISUALIZATION_CONFIG.DNA_LENGTH_VISUAL;
const SCALE = VISUALIZATION_CONFIG.SCALE_BP_TO_VISUAL;
const LOOP_PULSE_MS = VISUALIZATION_CONFIG.LOOP_PULSE_MS;
const EMISSIVE_PEAK = 2;
const EMISSIVE_NORMAL = 0.2;

interface SimulationViewerProps {
    engine: LoopExtrusionEngine;
    pulseLoops?: Loop[];
}

// Convert genome position to 3D coordinate
function genomeTo3D(position: number, genomeLength: number): number {
    return (position / genomeLength) * DNA_LENGTH - DNA_LENGTH / 2;
}

const DNAStrand = ({ genomeLength }: { genomeLength: number }) => {
    const points = useMemo(() => [
        new THREE.Vector3(genomeTo3D(0, genomeLength), 0, 0),
        new THREE.Vector3(genomeTo3D(genomeLength, genomeLength), 0, 0)
    ], [genomeLength]);
    
    const curve = new THREE.CatmullRomCurve3(points);

    return (
        <group>
            <mesh>
                <tubeGeometry args={[curve, 2, 0.2, 8, false]} />
                <meshStandardMaterial color="#444" />
            </mesh>
        </group>
    );
};

const CTCFMarker = ({ site, genomeLength }: { site: CTCFSite; genomeLength: number }) => {
    const x = genomeTo3D(site.position, genomeLength);
    
    // Forward CTCF: cone pointing right (>)
    // Reverse CTCF: cone pointing left (<)
    const rotation = site.orientation === 'F' 
        ? [0, 0, -Math.PI / 2] 
        : [0, 0, Math.PI / 2];
    
    const color = site.orientation === 'F' ? '#3498db' : '#e74c3c';
    
    return (
        <group position={[x, 0, 0]}>
            <mesh rotation={rotation as [number, number, number]}>
                <coneGeometry args={[0.15, 0.4, 16]} />
                <meshStandardMaterial color={color} />
            </mesh>
        </group>
    );
};

const LoopArc = ({ loop, genomeLength, pulsing }: { loop: Loop; genomeLength: number; pulsing: boolean }) => {
    const materialRef = useRef<THREE.MeshStandardMaterial>(null);
    const startTimeRef = useRef<number | null>(pulsing ? performance.now() : null);

    const curve = useMemo(() => {
        const startX = genomeTo3D(loop.leftAnchor, genomeLength);
        const endX = genomeTo3D(loop.rightAnchor, genomeLength);
        const midX = (startX + endX) / 2;
        const height = (endX - startX) / 2;

        return new THREE.QuadraticBezierCurve3(
            new THREE.Vector3(startX, 0, 0),
            new THREE.Vector3(midX, height, 0),
            new THREE.Vector3(endX, 0, 0)
        );
    }, [loop.leftAnchor, loop.rightAnchor, genomeLength]);

    useFrame(() => {
        const mat = materialRef.current;
        if (!mat || !pulsing) return;
        if (startTimeRef.current === null) startTimeRef.current = performance.now();
        const elapsed = (performance.now() - startTimeRef.current) / 1000;
        const t = Math.min(1, elapsed / (LOOP_PULSE_MS / 1000));
        mat.emissiveIntensity = EMISSIVE_NORMAL + (EMISSIVE_PEAK - EMISSIVE_NORMAL) * (1 - t);
    });

    return (
        <mesh>
            <tubeGeometry args={[curve, 20, 0.08, 8, false]} />
            <meshStandardMaterial
                ref={materialRef}
                color="#00f0ff"
                transparent
                opacity={0.6 + loop.strength * 0.4}
                emissive="#00f0ff"
                emissiveIntensity={pulsing ? EMISSIVE_PEAK : EMISSIVE_NORMAL}
            />
        </mesh>
    );
};

const CohesinComplex = ({
    engine,
    genomeLength
}: {
    engine: LoopExtrusionEngine;
    genomeLength: number;
}) => {
    const cohesins = engine.getCohesins();

    return (
        <group>
            {cohesins.map((cohesin, index) => {
                const leftX = genomeTo3D(cohesin.leftLeg, genomeLength);
                const rightX = genomeTo3D(cohesin.rightLeg, genomeLength);
                const centerX = (leftX + rightX) / 2;
                
                return (
                    <group key={index} position={[centerX, 0.3, 0]}>
                        {/* Left leg */}
                        <mesh position={[(leftX - centerX) / 2, 0, 0]}>
                            <sphereGeometry args={[0.1, 8, 8]} />
                            <meshStandardMaterial 
                                color={cohesin.active ? '#f39c12' : '#7f8c8d'}
                            />
                        </mesh>
                        {/* Right leg */}
                        <mesh position={[(rightX - centerX) / 2, 0, 0]}>
                            <sphereGeometry args={[0.1, 8, 8]} />
                            <meshStandardMaterial 
                                color={cohesin.active ? '#f39c12' : '#7f8c8d'}
                            />
                        </mesh>
                        {/* Connecting line */}
                        <line>
                            <bufferGeometry>
                                <bufferAttribute
                                    attach="attributes-position"
                                    count={2}
                                    array={new Float32Array([
                                        leftX - centerX, 0, 0,
                                        rightX - centerX, 0, 0
                                    ])}
                                    itemSize={3}
                                />
                            </bufferGeometry>
                            <lineBasicMaterial color="#f39c12" linewidth={2} />
                        </line>
                    </group>
                );
            })}
        </group>
    );
};

function isPulsing(loop: Loop, pulseLoops: Loop[]): boolean {
    return pulseLoops.some(p => p.leftAnchor === loop.leftAnchor && p.rightAnchor === loop.rightAnchor);
}

export const SimulationViewer = ({ engine, pulseLoops = [] }: SimulationViewerProps) => {
    const genomeLength = engine.genomeLength;
    const loops = engine.getLoops();
    const ctcfSites = engine.ctcfSites;

    return (
        <div style={{ width: '100%', height: '100%', background: '#000' }}>
            <Canvas camera={{ position: [0, 15, 30], fov: 60 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade />

                <DNAStrand genomeLength={genomeLength} />
                
                {/* CTCF Sites */}
                {ctcfSites.map((site, index) => (
                    <CTCFMarker 
                        key={index} 
                        site={site} 
                        genomeLength={genomeLength} 
                    />
                ))}
                
                {/* Formed Loops */}
                {loops.map((loop, index) => (
                    <LoopArc 
                        key={`loop-${index}`} 
                        loop={loop} 
                        genomeLength={genomeLength}
                        pulsing={isPulsing(loop, pulseLoops)}
                    />
                ))}
                
                {/* Active Cohesin */}
                <CohesinComplex engine={engine} genomeLength={genomeLength} />

                <OrbitControls 
                    enablePan={true}
                    enableZoom={true}
                    enableRotate={true}
                />
                <gridHelper args={[100, 100, 0x222222, 0x111111]} />
            </Canvas>
        </div>
    );
};
