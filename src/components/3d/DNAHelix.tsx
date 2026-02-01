import { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import * as THREE from 'three';

export interface DNAHelixProps {
    /** Number of base pairs along the helix */
    basePairs?: number;
    /** Twist angle per base pair (radians), ~2*PI/10.5 for B-DNA */
    twistPerBasePair?: number;
    /** Vertical rise per base pair */
    risePerBP?: number;
    /** Radius of the helix */
    radius?: number;
    /** Scale factor for the whole model */
    scale?: number;
}

const TUBE_RADIUS = 0.12;
const SPHERE_RADIUS = 0.15;
const H_BOND_RADIUS = 0.02;

function HelixScene({
    basePairs = 24,
    twistPerBasePair = (2 * Math.PI) / 10.5,
    risePerBP = 0.34,
    radius = 1.2,
    scale = 1,
}: DNAHelixProps) {
    const { backbone1, backbone2, basePositions1, basePositions2, hBonds } = useMemo(() => {
        const points1: THREE.Vector3[] = [];
        const points2: THREE.Vector3[] = [];
        const bases1: THREE.Vector3[] = [];
        const bases2: THREE.Vector3[] = [];
        const bonds: { p1: THREE.Vector3; p2: THREE.Vector3 }[] = [];

        for (let i = 0; i <= basePairs; i++) {
            const angle = i * twistPerBasePair;
            const y = i * risePerBP;
            const x1 = Math.cos(angle) * radius;
            const z1 = Math.sin(angle) * radius;
            const x2 = Math.cos(angle + Math.PI) * radius;
            const z2 = Math.sin(angle + Math.PI) * radius;
            points1.push(new THREE.Vector3(x1, y, z1));
            points2.push(new THREE.Vector3(x2, y, z2));
            bases1.push(new THREE.Vector3(x1, y, z1));
            bases2.push(new THREE.Vector3(x2, y, z2));
            if (i < basePairs) {
                const midY = y + risePerBP / 2;
                const midAngle = angle + twistPerBasePair / 2;
                bonds.push({
                    p1: new THREE.Vector3(Math.cos(angle) * radius, y, Math.sin(angle) * radius),
                    p2: new THREE.Vector3(Math.cos(angle + Math.PI) * radius, y, Math.sin(angle + Math.PI) * radius),
                });
            }
        }

        const curve1 = new THREE.CatmullRomCurve3(points1, false);
        const curve2 = new THREE.CatmullRomCurve3(points2, false);

        return {
            backbone1: curve1,
            backbone2: curve2,
            basePositions1: bases1,
            basePositions2: bases2,
            hBonds: bonds,
        };
    }, [basePairs, twistPerBasePair, risePerBP, radius]);

    const tubeSegments = Math.max(32, basePairs * 4);

    return (
        <group scale={scale}>
            {/* Backbone 1 — tubular, bioluminescent blue */}
            <mesh>
                <tubeGeometry args={[backbone1, tubeSegments, TUBE_RADIUS, 8, false]} />
                <meshStandardMaterial
                    color="#3399ff"
                    emissive="#1144aa"
                    emissiveIntensity={1.2}
                    roughness={0.2}
                    metalness={0.85}
                />
            </mesh>
            {/* Backbone 2 — tubular, bioluminescent purple */}
            <mesh>
                <tubeGeometry args={[backbone2, tubeSegments, TUBE_RADIUS, 8, false]} />
                <meshStandardMaterial
                    color="#9966ff"
                    emissive="#331166"
                    emissiveIntensity={1.2}
                    roughness={0.2}
                    metalness={0.85}
                />
            </mesh>

            {/* Base pair spheres — strand 1 cyan tint */}
            {basePositions1.map((pos, i) => (
                <mesh key={`b1-${i}`} position={pos}>
                    <sphereGeometry args={[SPHERE_RADIUS, 12, 12]} />
                    <meshStandardMaterial
                        color="#00ccff"
                        emissive="#0066aa"
                        emissiveIntensity={0.8}
                        roughness={0.3}
                        metalness={0.7}
                    />
                </mesh>
            ))}
            {/* Base pair spheres — strand 2 magenta tint */}
            {basePositions2.map((pos, i) => (
                <mesh key={`b2-${i}`} position={pos}>
                    <sphereGeometry args={[SPHERE_RADIUS, 12, 12]} />
                    <meshStandardMaterial
                        color="#cc66ff"
                        emissive="#6622aa"
                        emissiveIntensity={0.8}
                        roughness={0.3}
                        metalness={0.7}
                    />
                </mesh>
            ))}

            {/* Hydrogen bonds — thin tubes between strands */}
            {hBonds.map((bond, i) => {
                const curve = new THREE.LineCurve3(bond.p1, bond.p2);
                return (
                    <mesh key={`hb-${i}`}>
                        <tubeGeometry args={[curve, 4, H_BOND_RADIUS, 6, false]} />
                        <meshStandardMaterial
                            color="#ffffff"
                            emissive="#4488ff"
                            emissiveIntensity={0.5}
                            roughness={0.4}
                            metalness={0.6}
                        />
                    </mesh>
                );
            })}
        </group>
    );
}

export function DNAHelixViewer(props: DNAHelixProps) {
    const { basePairs = 24, scale = 1 } = props;
    const totalHeight = basePairs * (props.risePerBP ?? 0.34);
    const camZ = Math.max(15, totalHeight * scale * 0.8);

    return (
        <div className="w-full h-full min-h-[500px] bg-black relative rounded-xl overflow-hidden shadow-2xl border border-gray-800">
            <Canvas
                camera={{ position: [0, totalHeight * scale * 0.5, camZ], fov: 50 }}
                gl={{ antialias: true }}
                style={{ height: '100%' }}
            >
                <color attach="background" args={['#050510']} />
                <ambientLight intensity={0.4} />
                <pointLight position={[10, totalHeight * 0.5, 15]} intensity={2} />
                <pointLight position={[-10, totalHeight * 0.5, 10]} intensity={1} color="#4488ff" />
                <pointLight position={[5, 0, -5]} intensity={0.8} color="#8866ff" />
                <Stars radius={120} depth={60} count={6000} factor={4} saturation={0} fade speed={0.5} />
                <HelixScene {...props} />
                <OrbitControls enablePan enableZoom enableRotate />
            </Canvas>
            <div className="absolute bottom-4 left-4 text-white text-xs font-mono opacity-80">
                DNA Helix — drag to rotate, scroll to zoom
            </div>
        </div>
    );
}
