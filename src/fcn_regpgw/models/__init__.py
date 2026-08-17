"""Model architectures for FCN-RegPGW, ModAFNO, PrecipNet, and RegPGW."""

from fcn_regpgw.models.afno import AFNO, AFNO2DLayer, AFNOBlock, AFNOMlp, PatchEmbed
from fcn_regpgw.models.embeddings import (
    ModEmbedNet,
    OneHotEmbedding,
    PositionalEmbedding,
)
from fcn_regpgw.models.fft import imag, irfft2, real, rfft2, view_as_complex
from fcn_regpgw.models.global_fcn import GlobalFCNDrivingModel
from fcn_regpgw.models.lightning_module import FCNRegPGWLightningModule
from fcn_regpgw.models.modafno import (
    ModAFNO,
    ModAFNO2DLayer,
    ModAFNOBlock,
    ScaleShiftMlp,
)
from fcn_regpgw.models.precip_net import PrecipNet
from fcn_regpgw.models.regpgw_lightning import RegPGWLightningModule
from fcn_regpgw.models.regpgw_net import (
    RegPGWConvBlock,
    RegPGWNet,
    RegPGWSpectralBlock,
)

__all__ = [
    "AFNO",
    "AFNO2DLayer",
    "AFNOBlock",
    "AFNOMlp",
    "FCNRegPGWLightningModule",
    "GlobalFCNDrivingModel",
    "ModAFNO",
    "ModAFNO2DLayer",
    "ModAFNOBlock",
    "ModEmbedNet",
    "OneHotEmbedding",
    "PatchEmbed",
    "PositionalEmbedding",
    "PrecipNet",
    "RegPGWConvBlock",
    "RegPGWLightningModule",
    "RegPGWNet",
    "RegPGWSpectralBlock",
    "ScaleShiftMlp",
    "imag",
    "irfft2",
    "real",
    "rfft2",
    "view_as_complex",
]
