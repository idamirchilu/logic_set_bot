import logging
from io import BytesIO
import matplotlib.pyplot as plt
from sympy import latex

logger = logging.getLogger(__name__)


def latex_to_image(latex_str: str):
    """Convert LaTeX string to an image"""
    try:
        # Use Matplotlib mathtext (faster, no external TeX needed)
        plt.rcParams['text.usetex'] = False

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.text(0.5, 0.5, f'${latex_str}$', fontsize=16,
                ha='center', va='center')
        ax.axis('off')

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf
    except Exception as e:
        logger.error(f"Error converting LaTeX to image: {e}")
        return None