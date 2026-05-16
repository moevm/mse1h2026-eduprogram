import { useState } from "react";
import { motion } from "framer-motion";
import "./NavbarSelect.css";

export default function NavbarSelect({ options = [] }) {
    const [activeIndex, setActiveIndex] = useState(0);

    return (
        <div className="segmented-container">
            <div className="segmented-wrapper">
                <motion.div
                    className="segmented-slider"
                    initial={false}
                    animate={{
                        width: `calc(${(100 / options.length)}% - 10px)`,
                        left: `calc(${(100 / options.length) * activeIndex}% + 5px)`,
                    }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />

                {options.map((option, index) => (
                    <button
                        key={index}
                        className={`segmented-button ${index === activeIndex ? "active" : ""}`}
                        onClick={() => {
                            setActiveIndex(index);
                            option.onClick && option.onClick(option.value);
                        }}
                    >
                        {option.label}
                    </button>
                ))}
            </div>
        </div>
    );
}