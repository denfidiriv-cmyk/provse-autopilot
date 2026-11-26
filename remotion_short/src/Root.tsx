import { Composition, CalculateMetadataFunction } from "remotion";
import { Short, ShortProps } from "./Short";

const calc: CalculateMetadataFunction<ShortProps> = ({ props }) => ({
  durationInFrames: Math.max(30, Math.round(props.duration * 30)),
});

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Short"
    component={Short}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={600}
    calculateMetadata={calc}
    defaultProps={{ audio: "", duration: 20, accent: "#ffd60a", keywords: [], scenes: [], words: [], outro: { top: "УСЕ ПРО", acc: "СВІТ", bg: "#111", bg2: "#222", start: 18 } } as ShortProps}
  />
);
