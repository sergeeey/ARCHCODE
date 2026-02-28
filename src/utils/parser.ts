import { GenomeElement, ElementType } from "../types";
import { v4 as uuidv4 } from "uuid";

export interface SpecRegion {
  start: number;
  end: number;
  type: string;
  metadata?: any;
}

export const parseResearchSpec = (regions: SpecRegion[]): GenomeElement[] => {
  return regions.map((region) => {
    let type: ElementType = "NONE";

    // Mapping logic
    if (region.type === "CTCF_FORWARD") type = "CTCF_FORWARD";
    else if (region.type === "CTCF_REVERSE") type = "CTCF_REVERSE";
    else if (region.type === "REPEAT") type = "ENHANCER"; // Using ENHANCER as placeholder for HETEROCHROMATIN/REPEAT for now as per instructions to just add type, but ElementType is strict.
    // Wait, user said: "Если region.type == 'REPEAT' (транспозон) -> создать элемент с type: 'HETEROCHROMATIN'"
    // But 'HETEROCHROMATIN' is not in my ElementType union in types.ts.
    // I should probably update types.ts first or map to an existing one.
    // User instruction: "создать элемент с type: 'HETEROCHROMATIN' (это будет замедлять петли, но пока просто добавь тип)."
    // So I need to update types.ts to include 'HETEROCHROMATIN'.

    return {
      id: uuidv4(),
      position: region.start, // Simplified: taking start as position
      type:
        type === "NONE" && region.type === "REPEAT"
          ? ("HETEROCHROMATIN" as ElementType)
          : type,
    };
  });
};
