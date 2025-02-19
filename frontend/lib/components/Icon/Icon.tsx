import { IconContainer } from "./styles";
import { IconSize, IconType } from "./types";


type IconProps = {
    type: IconType;
    size: IconSize;
}

export const Icon: React.FC<IconProps> = ({ type, size }) => {
    return (
        <IconContainer type={type} size={size} />
    )
}