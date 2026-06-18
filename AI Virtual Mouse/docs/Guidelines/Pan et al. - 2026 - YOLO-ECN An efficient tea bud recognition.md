> YOLO-ECN: An efficient tea bud recognition model based on YOLOv10s
>
> Weidong Pan [<sup>a</sup>](#_bookmark0), Ce Liu <sup>[a](#_bookmark0),[\*](#_bookmark3)</sup>, Longzhe Quan [<sup>a</sup>](#_bookmark0), Xuanfu Du [<sup>c</sup>](#_bookmark2), Yan Song [<sup>a</sup>](#_bookmark0), Jingming Ning <sup>[a](#_bookmark0),[b](#_bookmark1)</sup>,
>
> Liqing Chen <sup>[a](#_bookmark0),[\*](#_bookmark3)</sup>
>
> <span id="_bookmark0" class="anchor"></span><sup>a</sup> *School of Engineering, Anhui Agricultural University, Hefei 230036, China*
>
> <span id="_bookmark1" class="anchor"></span><sup>b</sup> *State Key Laboratory of Tea Biology and Resource Utilization, Hefei 230036, China*
>
> <span id="_bookmark2" class="anchor"></span><sup>c</sup> *School of Intelligent Manufacturing, Anhui University of Applied Technology, Hefei 230011, China*
>
> A R T I C L E I N F O
>
> *Keywords:*
>
> Tea bud recognition YOLO-ECN
>
> EfficientnetV2-S network CAFM
>
> Loss function
>
> A B S T R A C T
>
> Efficient tea bud recognition is vitally important to improve the harvesting performance of premium tea. Numerous studies have been directed toward the development of recognition models. To overcome the computational limitations of edge devices without compromising recognition precision in complex tea garden environments, a recognition model entitled YOLO-ECN is proposed in this study. This model adopts the EfficientnetV2-S network as its backbone, employing a hierarchical lightweight design and a compound scaling strategy to simultaneously optimize the accuracy and parameter efficiency. To mitigate the missed detection, the Convolution and Attention Fusion Module (CAFM) is developed by incorporating an adaptive dynamic weighting strategy to strengthen the feature representation. Moreover, a hybrid loss function integrating the Normalized Wasserstein Distance and intersection over union is developed to improve the capture ability of occluded tea buds. Ablation experiments verify that the proposed YOLO-ECN achieves a precision of 88.4%, recall of 88.6% and mAP of 88.9%, which surpasses the original YOLOv10s model by 9.5 percentage points in precision, 4.4 percentage points in recall and 10.4 percentage points in mAP. The YOLO-ECN demonstrates a competitive combination of high accuracy and low computational cost compared to the mainstream models of Faster R-CNN, Tea-YOLO, YOLOv7MCS and YOLOv11n, providing an efficient recognition model for the automated picking of tea buds.

# Introduction

> Tea stands as one of the three major beverages worldwide, boasting a vast consumer base and serving as a crucial economic resource for many countries and regions \[[1](#_bookmark24)\]. With the global aging population and large-scale migration of rural labor, the traditional manual picking is confronted with increasing challenges of labor shortages and high costs, which increasingly fails to meet the production demands \[[2](#_bookmark25),[3](#_bookmark26)\]. There-fore, it is an urgent task to develop the intelligent tea picking platform. However, due to the inherent tea bud characteristics, such as small size and large quantity, the low color distinction between tea buds and old leaves and dense and occluded distribution in the complex tea garden scenarios \[[4](#_bookmark27),[5](#_bookmark28)\], the tea bud recognition faces significant challenges in achieving both high accuracy and low computational cost.
>
> To address tea bud detection in these challenging scenarios, a series of recognition methods have been proposed. Shao et al. employed the histogram equalization to highlight tea bud features, such as edge,
>
> contour and contrast information \[[6](#_bookmark29)\]. Zhang et al. applied the machine vision approach to distinguish the fresh tea buds and presented a real-time monitoring method of optimum harvesting time \[[7](#_bookmark30)\]. Zhang et al. used a watershed segmentation algorithm to enhance the identi-fication accuracy under the strong and uneven illumination environ-ment \[[8](#_bookmark31)\]. The vision-based recognition methods typically depend on chromatic and morphological tea bud features, which are generally
>
> time-consuming and sensitive to environmental conditions. With the deep learning widely applied in tea bud recognition \[[9–11](#_bookmark32)\], Chen et al. applied the Faster region-based Convolutional Neural Networks (CNN)
>
> to identify the tea buds of one tip with two leaves \[[12](#_bookmark33)\]. Pan et al. developed a Swin-Oriented R-CNN to identify tea buds and then local-ized the picking point utilizing semantic segmentation and traditional morphological analysis \[[13](#_bookmark34)\]. Recently, the YOLO-based algorithms have been widely adopted due to their excellent detection accuracy and ef-ficiency \[[14](#_bookmark35),[15](#_bookmark36)\]. Yang et al. \[[16](#_bookmark37)\] and Xu et al. \[[17](#_bookmark38)\] both developed YOLOv3 algorithm for tea bud recognition, which provides theoretical
>
> <span id="_bookmark3" class="anchor"></span>\* Corresponding authors.
>
> *E-mail addresses:* <liuce@ahau.edu.cn> (C. Liu), <lqchen@ahau.edu.cn> (L. Chen).
>
> <https://doi.org/10.1016/j.atech.2026.102048>
>
> Received 15 December 2025; Received in revised form 25 March 2026; Accepted 25 March 2026
>
> Available online 25 March 2026
>
> 2772-3755/© 2026 The Authors. Published by Elsevier B.V. This is an open access article under the CC BY license (<http://creativecommons.org/licenses/by/4.0/>).
>
> <span id="_bookmark4" class="anchor"></span>**Table 1**
>
> The setting parameters of camera.
>
> Variable Value/State
>
> Camera model SONY ZV-E10
>
> Image size 4240×2832 pixels
>
> Zoom No zoom
>
> Flash mode No flash
>
> Aperture *Av*. f/3.5
>
> Exposure time *Av*. 1/50s
>
> Focal length 35mm
>
> Operation mode Manual
>
> Macro Off
>
> Image type JPG
>
> and technological support for intelligent and accurate picking of high-quality tea. Chen et al. presented an improved YOLOv7 by intro-ducing the feature fusion module and selective kernel attention mech-anism, yielding a recognition accuracy of 90.99% \[[18](#_bookmark39)\]. Subsequently, Song et al. enhanced YOLOv7 with a dual-head design and morphology heatmap labels, enabling simultaneous detection of tea buds and their picking points \[[19](#_bookmark40)\]. The aforementioned studies markedly improve recognition accuracy for complicated tea garden circumstances. How-ever, restricted by computing capability of mobile terminals, the recognition models still need to be further optimized to settle calculation complexity problem.
>
> To improve the recognition efficiency, Gui et al. \[[20](#_bookmark41)\] and Li et al.
>
> \[[21](#_bookmark42)\] presented a lightweight tea bud detection model by introducing a Ghost_conv module to replace the standard convolution, significantly reducing the computational burden and model size. Wu et al. developed a multi-modal detection network based on YOLOv7, incorporating a parallel lightweight backbone to extract depth features and integrating a self-attention mechanism to prioritize contextual information \[[22](#_bookmark43)\]. Lu
>
> et al. constructed a Tea Bud DG model integrating the lightweight C3ghost module, Dynamic Head and adaptive α-CIoU loss function to optimize the feature extraction performance with fewer filters \[[23](#_bookmark44)\].
>
> Wang et al. developed the YOLOv5 model by employing lightweight ShuffleNetV2 network along with Bi-directional feature pyramid network and parameter-free attention module, reducing parameters by 83.7% and FLOPs by 85.6% \[[24](#_bookmark45)\]. The investigations have greatly improved the recognition efficiency by optimizing the convolution design.
>
> For the practical deployment of automated tea harvesting on resource-constrained edge devices, the detection module must achieve high accuracy with low computational cost. This study presents an improved recognition model based on YOLOv10s, which is named as YOLO-ECN. The benefits of YOLO-ECN are as follows:

1)  The backbone integrates an EfficientnetV2-S network, featuring a hierarchical lightweight design and a compound scaling strategy to balance the model dimension and recognition accuracy.

2)  An enhanced Convolution and Attention Fusion Module (CAFM) is embedded into the neck network, employing an adaptive dy-namic weighting strategy to optimize feature representation and improve detection performance of small tea buds in color-similar backgrounds.

3)  A hybrid loss function is developed by integrating the Normalized Wasserstein Distance (NWD) and complete intersection over union (CIoU) to address the sensitivity to positional deviations and improve the model robustness in overlap and occluded scenarios.

> The structure of this paper is outlined as follows. The tea bud dataset is established and the YOLO-ECN model is proposed in [Section 2](#discussions). [Section](#result-analysis) [3](#result-analysis) validates its effectiveness through ablation experiments and compar-ative experiments, demonstrating its capability to maintain high recognition accuracy with low computational cost. Section 4 discusses the experimental results to further illustrate the superiority of the pro-posed model. [Section 5](#conclusion) summarizes the main conclusions of this paper.

# Materials and methods

1.  *Dataset acquisition*

> The original tea bud images were collected hourly from 6:00 to 18:00 daily using a SONY ZV-E10 digital camera in the Agricultural Research Garden of Anhui Agricultural University. The setting parameters of camera are presented in [Table 1](#_bookmark4).
>
> A total of 3000 images were collected in this study and then parti-tioned into training, validation, and test sets at a ratio of 4:1:1. The dataset encompasses representative tea cultivars, such as Dragon-well tea, Huangshan Maojian, Xinyang Maojian, Anji White Tea and so on. Moreover, it also covers a variety of scenarios, characterized by the weather variability, tea bud complexity, shooting angle and illumination influence, as depicted in [Fig. 1(a)](#_bookmark5)-([d](#_bookmark5)).

2.  *Dataset processing*

> To strengthen the adaptability and robustness of recognition model, the original dataset is enriched via various data augmentation methods, consisting of geometric transformation, brightness adjustment and color contrast enhancement, as shown in [Fig. 2](#_bookmark6). The dataset is enlarged to 10,600 images.
>
> Afterwards, the images are manually annotated with LabelImg. The
>
> <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image1.jpeg" style="width:6.65624in;height:2.4in" />
>
> <span id="_bookmark5" class="anchor"></span>**Fig. 1.** Shooting locations and scenarios of original images from different varieties.
>
> <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image2.jpeg" style="width:6.66419in;height:1.07667in" />
>
> <span id="_bookmark6" class="anchor"></span>**Fig. 2.** Schematic representation of dataset augmentation methods.

<img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image3.jpeg" style="width:5.82153in;height:2.13in" />

> <span id="_bookmark7" class="anchor"></span>**Fig. 3.** Examples of tea bud annotation in different scenarios. (a) bright light, (b) weak light, (c) high-density distribution, (d) obstruction.

<img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image4.jpeg" style="width:6.64851in;height:4.47in" />

> <span id="_bookmark8" class="anchor"></span>**Fig. 4.** Network architecture of the YOLO-ECN model.
>
> labelling criterion is that each visually distinct and complete tea bud was annotated with a bounding box, and the tea buds that appear severely
>
> blurred were not taken into account. All annotation files were saved as TXT format. [Fig. 3](#_bookmark7) gives some annotated image examples of different
>
> <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image5.jpeg" style="width:6.65119in;height:1.64in" />
>
> <span id="_bookmark9" class="anchor"></span>**Fig. 5.** Schematic representation of Fused-MBConv and MBConv structures.
>
> <span id="_bookmark10" class="anchor"></span>**Table 2**
>
> Architecture of the EfficientnetV2-S backbone.

| Stage | Operator              | Stride | Channels | Layers |
|-------|-----------------------|--------|----------|--------|
| 0     | stem (Conv3×3)        | 2      | 24       | 1      |
| 1     | Fused-MBConv, k3×3    | 1      | 24       | 2      |
| 2     | Fused-MBConv, k3×3    | 2      | 48       | 4      |
| 3     | Fused-MBConv, k3×3    | 2      | 64       | 4      |
| 4     | MBConv, k3×3, SE=0.25 | 2      | 128      | 6      |
| 5     | MBConv, k3×3, SE=0.25 | 2      | 160      | 6      |
| 6     | MBConv, k3×3, SE=0.25 | 2      | 256      | 6      |
| 7     | SPPF & PSA            | \-     | 1024     | 2      |

> scenarios.

3.  *Improvement of YOLOv10s model*

> Given the YOLOv10s model achieves faster inference by eliminating the non-maximum suppression post-processing while maintaining adaptability for edge devices through multi-scale feature fusion \[[25](#_bookmark46)\]. However, it is inadequate to cope with complex tea garden environ-ments due to the challenges of small tea buds, high-density distributions and frequent occlusions. To surmount these limitations, we propose the YOLO-ECN with the YOLOv10s as the base network. In the YOLO-ECN, the lightweight EfficientnetV2-S is implemented, an improved CAFM module is introduced and the loss function is also developed by inte-grating the NWD and CIoU. The network architecture of YOLO-ECN is shown as [Fig. 4](#_bookmark8).

1.  *EfficientnetV2-S network structure*

> To reduce the model size and facilitate the deployment on embedded platforms, a lightweight EfficientnetV2-S network is adopted to replace the original backbone network, which employs a hierarchical design by integrating Fused MBConv and MBConv modules, as illustrated in [Fig. 5](#_bookmark9). A training-aware neural architecture search is adopted to simulta-neously optimize the accuracy, parameter efficiency and training effi-ciency \[[26](#_bookmark47)\]. The concrete architecture details of EfficientnetV2-S
>
> backbone are summarized in [Table 2](#_bookmark10).
>
> In the shallow network, the Fused MBConv module utilizes 3 × 3 standard convolution to capture low-level tea bud features and reduce the computational cost in the early stage. In the deep network, the
>
> MBConv module is employed to extract high-level tea bud features using the 3 × 3 depthwise convolution and 1 × 1 expanded convolution. Both Fused MBConv and MBConv modules encompass the SE channel atten-
>
> tion mechanism to refine the feature learning and representation ca-pacity. And the SiLU activation function is employed to alleviate the gradient vanishing and overfitting issues. Moreover, a compound scaling strategy is developed to simultaneously optimize the depth, width and resolution, thus dramatically reducing the model parameters and computational burdens without sacrificing its feature extraction ability and recognition accuracy.

2.  *Improved CAFM*

> To overcome the challenges posed by the small size and high back-ground similarity of tea buds, given the CAFM enables modelling of both global and local features \[[27](#_bookmark48)\], the CAFM is further improved with an adaptive weighting strategy to dynamically fuse global and local fea-tures. Moreover, a Drop Path regularization is used to randomly discard
>
> the fusion results with a probability of *p* = 0.15, effectively preventing
>
> overfitting and enhancing the generalization ability. The structure of developed AD-CAFM is given in [Fig. 6](#_bookmark11).
>
> In the local branch, a 1 × 1 2D convolution is first used to modulate
>
> the channel dimensions, followed by a channel shuffle operation to fuse multi-channel information, eliminating the feature isolation and enhancing the feature extraction ability. Subsequently, a 3 × 3 × 3 3D
>
> convolution is utilized to capture local features and edge information of
>
> tea buds, resulting in the local branch output *F*<sub>conv</sub>, which can be expressed as
>
> *F*<sub>conv</sub> = W<sub>3×3×3</sub>(CS(W<sub>1×1</sub>(*X<sub>in</sub>*))) (1)
>
> where W<sub>3×3</sub> <sub>×</sub> <sub>3</sub>, W<sub>1×1</sub> denote 3D and 2D convolution, respectively. CS is the channel shuffle operation, *X<sub>in</sub>* represents the input feature maps of tea buds.
>
> <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image6.jpeg" style="width:5.81564in;height:1.64667in" />
>
> <span id="_bookmark11" class="anchor"></span>**Fig. 6.** Schematic representation of the AD-CAFM structure.
>
> The global branch adopts an attention branch to capture the broader contextual information of tea buds. The query (**Q**), key (**K**) and value (**V**)
>
> <span id="_bookmark12" class="anchor"></span>**Table 3**
>
> Experiment environment.
>
> tensors with a shape of
>
> ∧ ∧ ∧
>
> × × are generated through a 1 × 1
>
> Configuration Parameters
>
> *H W C*
>
> convolution and three 3 × 3 depthwise separable convolutions, and then
>
> ∧ ∧ ∧
>
> reshaped to **Q**, **K** and **V**, respectively. The attention maps are constructed
>
> ∧ ∧ ∧
>
> by the interaction of **Q** and **K**, then multiplied by **V** in a matrix fashion to

*Q*, *K*, *V*

obtain the global importance distribution. Finally, a 1 × 1 2D convo-lution is utilized to modulate the channel dimensions. The result is fused with initial feature maps to produce the global branch output *F*<sub>att</sub>

> CPU 16vCPU Intel(R) Xeon(R) Platinum 8481C
>
> GPU RTX4090D (24 GB)
>
> Compilation language Python 3.9
>
> Memory 60 GB
>
> Software platform PyTorch 1.9.0
>
> Operating system Windows11

att

*F* = *W*

∧ ∧

1×1

Attention(

> ∧ ) + *X*
>
> \(2\)
>
> <span id="_bookmark13" class="anchor"></span>**Table 4**

Comparison of different lightweight networks.

in

(*Q*, *K*, *V*

)

∧ ∧ ∧

> where Attention
>
> ∧ ∧

= *V*

Softmax

> ∧ *ε*), *ε* is a learnable scaling

<table style="width:47%;">
<caption><p>(<em>KQ</em>/</p></caption>
<colgroup>
<col style="width: 14%" />
<col style="width: 10%" />
<col style="width: 12%" />
<col style="width: 9%" />
</colgroup>
<thead>
<tr>
<th>Model</th>
<th style="text-align: center;">mAP</th>
<th><blockquote>
<p>Params/M</p>
</blockquote></th>
<th><blockquote>
<p>FLOPs/G</p>
</blockquote></th>
</tr>
</thead>
<tbody>
<tr>
<td>Original YOLOv10s</td>
<td style="text-align: center;">78.5%</td>
<td><blockquote>
<p>7.21</p>
</blockquote></td>
<td><blockquote>
<p>21.6</p>
</blockquote></td>
</tr>
<tr>
<td>+MobileNetV3</td>
<td style="text-align: center;">76.1%</td>
<td><blockquote>
<p>4.96</p>
</blockquote></td>
<td><blockquote>
<p>15.5</p>
</blockquote></td>
</tr>
<tr>
<td>+ShuffleNetV2</td>
<td style="text-align: center;">74.7%</td>
<td><blockquote>
<p>6.11</p>
</blockquote></td>
<td><blockquote>
<p>16.3</p>
</blockquote></td>
</tr>
<tr>
<td>+SqueezeNet1.1</td>
<td style="text-align: center;">73.8%</td>
<td><blockquote>
<p>3.89</p>
</blockquote></td>
<td><blockquote>
<p>12.1</p>
</blockquote></td>
</tr>
<tr>
<td>+EfficientnetV2-S</td>
<td style="text-align: center;">79.4%</td>
<td><blockquote>
<p>5.32</p>
</blockquote></td>
<td><blockquote>
<p>14.7</p>
</blockquote></td>
</tr>
</tbody>
</table>

coefficient to restrict the attention weights.

> The superiority over the original CAFM is that the AD-CAFM can optimize the feature representation by dynamically fusing the global and local features via a 1 × 1 convolution. The final multi-scale feature
>
> output is represented as
>
> *F*out = *Wl* ⊗ *F*conv + *Wg* ⊗ *F*att (3)
>
> where ⊗ denotes element-wise multiplication. *W<sub>l</sub>* and *W<sub>g</sub>* are the weighting coefficients for local branch and global branch, respectively, which can be adaptively adjusted based on the initial tea bud feature
>
> maps \[[28](#_bookmark49),[29](#_bookmark50)\].
>
> \[*W<sub>l</sub>*, *W<sub>g</sub>*\] = Softmax(C<sub>1×1</sub> *X*<sub>in</sub>)) (4)
>
> where C<sub>1×1</sub> represents a 1 × 1 convolution. The Softmax function is applied for inter-branch fusion rather than intra-branch modulation.

3.  *Hybrid loss function*

> Since the original intersection over union (IoU) loss function exhibits high sensitivity on tea bud size and fails to provide the gradient infor-
>
> where *C* is a constant depending on the dataset. Taking into account the modelling and evaluation procedure of NWD may impede the conver-gence speed \[[30](#_bookmark51),[32](#_bookmark53)\], a hybrid loss function is proposed by integrating the NWD and CIoU, which is given as
>
> *L<sub>H</sub>* = *λ<sub>N</sub>L<sub>N</sub>* + (1 — *λ<sub>N</sub>*)⋅*L<sub>C</sub>* (9)
>
> where λN signifies the weight coefficient for the NWD loss.

4.  *Assessment indicators*

> To quantitatively assess the tea bud recognition performance of different models, several accuracy indicators consisting of Precision (P), Recall (R) and mean Average Precision (mAP) are adopted, which are defined as
>
> mation for network optimization when the recognition box has no intersection with the true or completely covers the others \[[30](#_bookmark51),[31](#_bookmark52)\], the NWD loss function is embedded to enhance the capture capability for the
>
> overlap or occlusion scenarios, in which the bounding box *R*=(*x, y, w, h*)
>
> is represented as the 2D Gaussian distribution *N*(***μ*, ∑**).
>
> P = *TR TR* + *FD*
>
> R = *TR TR* + *FM*
>
> \(10\)
>
> \(11\)

*y*

***μ*** = \[ *x* \] (5)

1 ∑

*C*

> mAP = <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image7.png" />
>
> *C i*=1
>
> *AP<sub>i</sub>* (12)

0

⎡ *w*2 ⎤

2

<figure>
<img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image8.png" style="width:0.10551in" />
<figcaption><p>⎣ 0 <em>h</em> ⎦</p></figcaption>
</figure>

∑ = ⎢⎢ 4 ⎥⎥

4

> \(6\)
>
> where *TR, FM* and *FD* denote the numbers of tea buds that are correctly recognized, missed and wrongly detected, respectively. The recognition speed and deployment ability are represented by parameters (Params), floating-point operations (FLOPs) and frames per second (FPS).
>
> where (*x, y*), *w* and *h* respectively denote the center coordinate of bounding box, width and height. Therefore, the similarity between the recognized and true boxes can be quantified by the distributional dis-tance, which can be expressed as

\
Result analysis
===============

> The network training was performed using Python 3.9. The experi-
>
> mental environment is detailed in [Table 3](#_bookmark12). All input images were stan-dardized to a resolution of 640×640. The model was trained for 200
>
> (\[ *<u>w</u> h* \]<sub>T</sub> \[
>
> *w h* \]T) 2

2

*W*<sup>2</sup>(*N*<sub>r</sub>, *N<sub>t</sub>*) = ‖

> *x<sub>r</sub>*, *y<sub>r</sub>*, *<sup>r</sup>* <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image9.png" />*<sup>r</sup>*

,

2 2

> , *x<sub>t</sub>*, *y<sub>t</sub>*, *<sup>t</sup> <sup>t</sup>* ‖
>
> 2 2

2

> \(7\)
>
> epochs with a batch size of 32, employing the SGD optimizer with a

,

momentum of 0.937. The learning rate was initialized at 0.01 and decayed to 0.001 using cosine annealing. The model inference was

2

where *W*<sup>2</sup>(*N*<sub>r</sub>, *N*<sub>t</sub>) represents the second-order Wasserstein distance of

2

two Gaussian distributions, ‖ ‖<sup>2</sup> represents the Euclidean norm. The exponential normalization is applied to Wasserstein distance, which yields

> executed at FP32 precision without any mixed-precision acceleration. The batch size was fixed to 1 (BS=1) for consistent latency measurement.

1.  *Lightweight experiment*

2

⎛ √̅*W*̅̅̅̅2̅̅(̅̅*N*̅̅̅r̅̅,̅̅*N*̅̅̅t̅̅)̅̅⎞

> *NWD*(*N*<sub>r</sub>, *N*<sub>t</sub>) = exp⎝ — *C* ⎠ (8)
>
> To demonstrate the effectiveness of EfficientnetV2-S backbone on improving the recognition efficiency of tea buds, the MobileNetV3, ShuffleNetV2 and SqueezeNet1.1 modules are selected for
>
> <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image10.jpeg" style="width:3.31679in;height:2.40333in" />
>
> <span id="_bookmark15" class="anchor"></span>**Fig. 7.** Visual illustration of different lightweight networks.
>
> comprehensive comparison with the original YOLOv10s as the base network. The corresponding mAP, Params and FLOPs of different lightweight networks are listed in [Table 4](#_bookmark13).
>
> One can see that compared to the original YOLOv10s, the lightweight networks significantly reduce the model complexity. Although the EfficientnetV2-S has the Params of 5.32 M due to its hierarchical design, it achieves a lower FLOPs of 14.7 G, which is 5.2% and 9.8% lower than MobileNetV3 and ShuffleNetV2, respectively. And the EfficientnetV2-S achieves the highest mAP of 79.4% for its compound scaling strategy, outperforming the SqueezeNet1.1 by 7.6%. [Fig. 7](#_bookmark15) visually compares the recognition accuracy and computational cost across different light-weight models, demonstrating that the EfficientnetV2-S network ach-ieves the highest mAP while maintaining competitive computational cost.

2.  *Ablation experiment*

> In order to justify the validity of each improved module of YOLO-ECN, ablation experiments are carried out with the results being listed in [Table 5](#_bookmark16). Since the availability of EfficientNetV2-S has been proved in the lightweight experiment, we will not go into much detail here.

1.  *Validation of AD-CAFM*

> It can be concluded from [Table 5](#_bookmark16) that compared to the YOLO-E, the introduction of AD-CAFM slightly increases the Params and FLOPs. But its mAP is increased by 6.7%, reaching to 84.9%, which is mainly attributed to its adaptive dynamic weighting strategy. Moreover, due to the addition of Drop Path regularization, the R is also improved by 2.3%. [Fig. 8](#_bookmark17) shows a comparison of recognition heat maps among different models.
>
> It can be observed that the original YOLOv10s is insensitive to small tea buds, especially for high-density scenarios. Although the CAFM en-hances the focus on small tea buds, it tends to misallocate attentions to mature leaves and background clutter. The reason appears to be the performance degradation under the high-density environment. In contrast, the AD-CAFM integrates the self-tuning strategy and Drop Path module, effectively improving the suppression ability of background noise. The results of [Fig. 8(d)](#_bookmark17) demonstrate its superior performance in detecting small-size tea buds under color-similar backgrounds.

2.  *Validation of the hybrid loss function*

> In this ablation experiment, the weight coefficient λₙ for hybrid loss function is set to 0.7. As seen from [Table 5](#_bookmark16), the improved hybrid loss function with the YOLO-EC as the basis model has no influence on the
>
> Params and FLOPs with the P, R and mAP improved by 4.1%, 2.7% and 2.9%, respectively. [Fig. 9](#_bookmark18) illustrates the comparison of recognition re-sults among the CIoU, NWD and the hybrid loss function under the overlapped scenarios.
>
> It can be seen from [Fig. 9(b)](#_bookmark18) that the YOLO-EC using the CIoU loss function presents cluttered recognition boxes. Conversely, the recogni-tion boxes shown in [Figs. 9(c) and 9(d)](#_bookmark18) are clear and accurate with the mAP being 87.8% and 88.9%, respectively, apparently outperforming
>
> the CIoU loss function with mAP = 86.4%, especially for those over-
>
> lapping and occluded tea bud regions, which indicates that the NWD loss function exhibits superior performance for the overlapped tea bud recognition.
>
> [Fig. 10](#_bookmark19) presents the mAP and loss curves of above-mentioned loss functions. It can be seen from [Fig. 10(a)](#_bookmark19) that compared to the CIoU, the NWD loss function significantly enhances the recognition accuracy. However, the convergence speed is slightly slowed, requiring approxi-mately 100 iterations to converge. In comparison, the improved hybrid loss function not only maintains high recognition accuracy, but also notably accelerates convergence, which begins to converge after 35
>
> <span id="_bookmark16" class="anchor"></span>**Table 5**
>
> Results of ablation experiments.

<table style="width:98%;">
<colgroup>
<col style="width: 11%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 12%" />
<col style="width: 11%" />
<col style="width: 11%" />
<col style="width: 13%" />
<col style="width: 9%" />
</colgroup>
<thead>
<tr>
<th>Model</th>
<th style="text-align: center;">E</th>
<th style="text-align: center;">C</th>
<th style="text-align: center;">N</th>
<th><blockquote>
<p>Precision</p>
</blockquote></th>
<th style="text-align: center;">Recall</th>
<th style="text-align: center;">mAP</th>
<th><blockquote>
<p>Params/M</p>
</blockquote></th>
<th><blockquote>
<p>FLOPs/G</p>
</blockquote></th>
</tr>
</thead>
<tbody>
<tr>
<td>Original</td>
<td style="text-align: center;">×</td>
<td style="text-align: center;">×</td>
<td style="text-align: center;">×</td>
<td><blockquote>
<p>78.9%</p>
</blockquote></td>
<td style="text-align: center;">84.2%</td>
<td style="text-align: center;">78.5%</td>
<td><blockquote>
<p>7.21</p>
</blockquote></td>
<td><blockquote>
<p>21.6</p>
</blockquote></td>
</tr>
<tr>
<td>YOLO-E</td>
<td style="text-align: center;">√</td>
<td style="text-align: center;">×</td>
<td style="text-align: center;">×</td>
<td><blockquote>
<p>79.6%</p>
</blockquote></td>
<td style="text-align: center;">84.4%</td>
<td style="text-align: center;">79.4%</td>
<td><blockquote>
<p>5.32</p>
</blockquote></td>
<td><blockquote>
<p>14.7</p>
</blockquote></td>
</tr>
<tr>
<td>YOLO-EC</td>
<td style="text-align: center;">√</td>
<td style="text-align: center;">√</td>
<td style="text-align: center;">×</td>
<td><blockquote>
<p>84.9%</p>
</blockquote></td>
<td style="text-align: center;">86.3%</td>
<td style="text-align: center;">86.4%</td>
<td><blockquote>
<p>5.92</p>
</blockquote></td>
<td><blockquote>
<p>14.9</p>
</blockquote></td>
</tr>
<tr>
<td>YOLO-ECN</td>
<td style="text-align: center;">√</td>
<td style="text-align: center;">√</td>
<td style="text-align: center;">√</td>
<td><blockquote>
<p>88.4%</p>
</blockquote></td>
<td style="text-align: center;">88.6%</td>
<td style="text-align: center;">88.9%</td>
<td><blockquote>
<p>5.92</p>
</blockquote></td>
<td><blockquote>
<p>14.9</p>
</blockquote></td>
</tr>
</tbody>
</table>

> *Note*: √ represents that the module is adopted, × represents that the module is not adopted. E denotes the EfficientnetV2-S module, C is the AD-CAFM, N indicates the hybrid loss function.

<img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image11.jpeg" style="width:5.82612in;height:1.34667in" />

> <span id="_bookmark17" class="anchor"></span>**Fig. 8.** Comparisons of recognition heat maps of tea buds among different models. a) Original image, b) Original YOLOv10s, c) YOLO-E with the CAFM, d) YOLO-E with the AD-CAFM.
>
> <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image12.jpeg" style="width:4.98748in;height:3.82333in" />
>
> <span id="_bookmark18" class="anchor"></span>**Fig. 9.** Representation of recognition results of different loss functions under the overlapped scenarios. a) Original image, b) CIoU loss function, c) NWD loss function, d) Hybrid loss function.

<img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image13.jpeg" style="width:5.82071in;height:2.23in" />

> <span id="_bookmark19" class="anchor"></span>**Fig. 10.** Performance comparison of different loss functions (a) mAP, (b) box loss.
>
> <span id="_bookmark20" class="anchor"></span>**Table 6**
>
> Comparisons with the predominant recognition models.

3.  *Performance comparison with predominant models*

<table style="width:99%;">
<colgroup>
<col style="width: 7%" />
<col style="width: 8%" />
<col style="width: 5%" />
<col style="width: 5%" />
<col style="width: 7%" />
<col style="width: 6%" />
<col style="width: 6%" />
<col style="width: 51%" />
</colgroup>
<thead>
<tr>
<th>Model</th>
<th><blockquote>
<p>Precision</p>
</blockquote></th>
<th>Recall</th>
<th>mAP</th>
<th>Params/ M</th>
<th>FLOPs/ G</th>
<th>FPS/ (BS=1)</th>
<th><blockquote>
<p>terms of the recognition accuracy and computational cost for various tea garden scenarios, several predominant recognition models are adopted</p>
</blockquote></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

To further examine the availability and superiority of YOLO-ECN in

<table style="width:47%;">
<colgroup>
<col style="width: 9%" />
<col style="width: 7%" />
<col style="width: 5%" />
<col style="width: 5%" />
<col style="width: 6%" />
<col style="width: 6%" />
<col style="width: 6%" />
</colgroup>
<thead>
<tr>
<th>Faster R-</th>
<th>90.4%</th>
<th style="text-align: center;">88.4%</th>
<th style="text-align: center;">89.4%</th>
<th>147.84</th>
<th>317.8</th>
<th>49</th>
</tr>
</thead>
<tbody>
<tr>
<td><blockquote>
<p>CNN</p>
</blockquote></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
<tr>
<td>Tea-YOLO</td>
<td>86.2%</td>
<td style="text-align: center;">71.1%</td>
<td style="text-align: center;">85.2%</td>
<td>11.35</td>
<td>6.6</td>
<td>101</td>
</tr>
<tr>
<td>YOLOv7MCS</td>
<td>88.3%</td>
<td style="text-align: center;">87.4%</td>
<td style="text-align: center;">88.5%</td>
<td>25.37</td>
<td>51.7</td>
<td>72</td>
</tr>
<tr>
<td>YOLOv11n</td>
<td>79.6%</td>
<td style="text-align: center;">78.5%</td>
<td style="text-align: center;">81.6%</td>
<td>2.53</td>
<td>6.3</td>
<td>119</td>
</tr>
<tr>
<td>YOLO-ECN</td>
<td>88.4%</td>
<td style="text-align: center;">88.6%</td>
<td style="text-align: center;">88.9%</td>
<td>5.92</td>
<td>14.9</td>
<td>110</td>
</tr>
</tbody>
</table>

> iterations.
>
> According to the analysis hereinbefore, the proposed YOLO-ECN achieves high recognition accuracy with low computational cost, demonstrating its effectiveness under complex tea garden scenarios.
>
> for comparative experiments, including Faster R-CNN, Tea-YOLO \[[23](#_bookmark44)\], YOLOv7MCS \[[33](#_bookmark54)\] and YOLOv11n. The results are summarized in [Table 6](#_bookmark20).
>
> One can observe that the Faster R-CNN achieves higher accuracy, while suffering from larger model parameters, confirming the tradi-tional two-stage detection models generally have higher computational complexity and lower inference speed \[[34](#_bookmark55)\]. In comparison, the YOLO-based models achieve high accuracy with lower computational cost. Although the YOLO-ECN has relatively higher Params and FLOPs compared to the YOLOv11n, which is mainly attributed to the hierar-chical backbone design, it achieves a 76.7% reduction in Params and a
>
> <img src="AI Virtual Mouse/docs/Guidelines/pan_2026_yolo_ecn_md_media/media/image14.jpeg" style="width:6.65406in;height:5in" />
>
> <span id="_bookmark21" class="anchor"></span>**Fig. 11.** Representation of the recognition results of different models. a) Low light, b) High light, c) Occlusion, d) High-density distributions.
>
> 71.2% decrease in FLOPs compared to YOLOv7MCS. Compared with Tea-YOLO, the YOLO-ECN has 55.7% higher in FLOPs, but its Params are reduced by 47.8%, and its FPS is improved by 8.2%. Furthermore, the YOLO-ECN achieves the highest mAP, outperforming the Tea-YOLO, YOLOv7MCS and YOLOv11n by 4.2%, 0.4% and 8.2%, respectively.
>
> For validation across various tea garden scenarios, the proposed YOLO-ECN is applied to the tea bud images of four representative sce-narios randomly chosen from validation dataset, consisting of weak light, bright light, occluded and high-density distributions. The perfor-mance comparison among the above-mentioned models is shown in [Fig. 11](#_bookmark21).
>
> For the weak and bright light scenarios, the YOLO-ECN demonstrates greater sensitivity to the small-size tea buds, with merely one missed detection under the weak light scenario. When the tea buds suffer from partial and heavy occlusion, as displayed in [Fig. 11(c)](#_bookmark21), the YOLO-ECN significantly outperforms other models in recognition accuracy, which is mainly attributed to that the hybrid loss function can address the sensitivity to positional deviations. Furthermore, since the developed AD-CAFM incorporates an adaptive dynamic weighting strategy to enhance feature representation, the YOLO-ECN has only one false detection in case of the densely distributed circumstance without missed detections, as illustrated in [Fig. 11(d)](#_bookmark21). The visualized results confirm its higher precision and stronger robustness of the proposed YOLO-ECN, which is available to detect tea buds across various scenarios.

# Discussions

> Different from other crops, such as tomato, strawberry and
>
> wolfberry, which can be recognized by the color or shape, the tea bud harvesting faces unique challenges, such as small size and large quan-tity, the low color distinction with surrounding environment and dense and occluded distribution. Although extensive studies have been con-ducted to improve recognition accuracy for automatic harvesting, balancing this accuracy with the limited computational capacity of mobile terminals remains a critical bottleneck for real-world deploy-ment, especially when the embedded processor needs to simultaneously handle multiple demanding tasks, including visual servoing, path planning and motion control \[[35](#_bookmark56),[36](#_bookmark57)\].
>
> This study successfully addresses this dilemma by proposing the YOLO-ECN. Rather than simply pursuing the highest absolute precision, our approach focuses on minimizing the computational cost while maintaining highly competitive recognition accuracy for edge device deployment. Compared with the existing models, the proposed model yields a 5.7% improvement in mAP over Bai et al. \[[37](#_bookmark58)\] while reducing Params and FLOPs by 47.4% and 13.4%, respectively. Although the model by Yu et al. \[[38](#_bookmark59)\] achieved lower computational costs with the
>
> 2.58 M Params and 10.9 G FLOPs, our YOLO-ECN provides a 4.7% higher mAP. In contrast, while the complex models like Wang et al. \[[39](#_bookmark60)\] achieved a remarkable mAP of 95.73%, their massive computational burden (14.82 M Params, 34.4 G FLOPs) hinders real-time edge computing. Thus, the YOLO-ECN provides a more practical and high-precision visual support for automated tea bud harvesting.
>
> However, there are still some limitations in the present study. Firstly, the generalization of the proposed AD-CAFM module and hybrid loss function remains to be validated across different backbone architec-tures, as they were exclusively evaluated using the EfficientNetV2-S.
>
> Moreover, performance bottlenecks persist under the complex and variable tea garden scenarios, some false and missed tea bud detections still occur under the severely weak light and highly dense distribution, as illustrated in [Figs. 11(a)](#_bookmark21) and ([d](#_bookmark21)). Therefore, more robust algorithms and multi-modal sensory fusion will be the focus of our future work to further enhance generalization in real tea garden scenarios.

# Conclusion

> To overcome the bottleneck of deploying high-precision recognition models on computationally constrained edge devices, this study pro-poses an efficient tea bud recognition model, YOLO-ECN, which ach-ieves high recognition accuracy with minimized computational cost. This model employs the EfficientnetV2-S lightweight backbone, in-tegrates the AD-CAFM and incorporates the improved hybrid loss function combining NWD and CIoU, effectively addressing the issues stemming from the color-similar backgrounds and highly overlapping and densely distributed tea buds. Experimental results demonstrate that the proposed YOLO-ECN achieves a fast inference speed of 110 FPS with only 5.92 M parameters and 14.9 G FLOPs, while simultaneously maintaining a high mAP of 88.9%. Compared with the current pre-dominant models, the YOLO-ECN exhibits faster recognition speed and lower resource consumption, but also proves stronger robustness across various tea garden scenarios. This research provides a highly practical and efficient visual recognition algorithm, laying a solid technological foundation for the performance improvement of tea bud picking robots.

# Ethics statement

> Not applicable: This manuscript does not include human or animal research.

# CRediT authorship contribution statement

> **Weidong Pan:** Writing – original draft. **Ce Liu:** Funding acquisition, Conceptualization. **Longzhe Quan:** Investigation, Conceptualization. **Xuanfu Du:** Writing – review & editing, Funding acquisition. **Yan Song:** Validation, Funding acquisition. **Jingming Ning:** Writing – review &
>
> editing, Visualization, Supervision. **Liqing Chen:** Visualization, Methodology.

# Declaration of competing interest

> The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Acknowledgements

> The financial supports of the State Key Laboratory of Tea Biology and Resource Utilization (No. SKLTOF20230123), Natural Science Research Project of Anhui Province (No. 2024AH050880) and Anhui Provincial Natural Science Foundation (No. 2308085MC84) are gratefully acknowledged.

# Data availability

> Data will be made available on request.

# References

1.  [Y.G. Sun, Z.H. Li, H.P. Guo, Y. Feng, Y.Q. Tang, W.S. Zhang, J.Q. Gu, TDDet: a](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0001)

> [novel lightweight and efficient tea disease detector, Comput. Electron. Agric. 237](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0001) [(2025) 110481](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0001).

2.  [V.G. Dhanya, A. Subeesh, N.L. Kushwaha, D.K. Vishwakarma, T.N. Kumar,](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0002)

> [G. Ritika, A.N. Singh, Deep learning based computer vision approaches for smart](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0002) [agricultural applications, Artif. Intell. Agric. 6 (2022) 211–229](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0002).

3.  <span id="_bookmark26" class="anchor"></span>[X.Y. Zhao, L.Y. He, Y.T. Li, J.N. Chen, C.Y. Wu, Kinetostatic modeling of clam force](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0003) [in a tendon-driven soft robotic gripper for tea shoot plucking, Comput. Electron.](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0003) [Agric. 236 (2025) 110441](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0003).

4.  [T. Wang, K.M. Zhang, W. Zhang, R.Q. Wang, S.M. Wan, Y. Rao, Z.H. Jiang, L.C. Gu,](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0004) [Tea picking point detection and location based on mask-RCNN, Inf. Process. Agric.](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0004) [10 (2) (2023) 267–275](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0004).

5.  [G.C. Lin, J.T. Xiong, R.M. Zhao, X.M. Li, H.G. Hu, L.X. Zhu, R.H. Zhang, Efficient](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0005)

> [detection and picking sequence planning of tea buds in a high-density canopy,](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0005) [Comput. Electron. Agric. 213 (2023) 108213](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0005).

6.  [P.D. Shao, M.H. Wu, X.W. Wang, J. Zhou, S. Liu, Research on the tea bud](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0006) [recognition based on improved k-means algorithm, MATEC Web. Conf. 232 (2018)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0006) [03050](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0006).

7.  [L. Zhang, H.D. Zhang, Y.D. Chen, S.H. Dai, X.M. Li, I. Kenji, Z.H. Liu, M. Li, Real-time monitoring of optimum timing for harvesting fresh tea leaves based on](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0007) [machine vision, Int. J. Agric. Biol. Eng. 12 (1) (2019) 6–9](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0007).

8.  [L. Zhang, L. Zou, C.Y. Wu, J.M. Jia, J.N. Chen, Method of famous tea sprout](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0008)

> [identification and segmentation based on improved watershed algorithm, Comput.](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0008) [Electron. Agric. 184 (2021) 106108](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0008).

9.  [Y.X. Fu, H.C. Zheng, Z.B. Wang, J.Y. Huang, W. Fu, Detection of multi-class](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0009) [coconut clusters for robotic picking under occlusion conditions, Int. J. Agric. Biol.](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0009) [Eng. 18 (1) (2025) 267–278](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0009).

10. [K. Jha, A. Doshi, P. Patel, M. Shah, A comprehensive review on automation in](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0010)

> [agriculture using artificial intelligence, Artif. Intell. Agric. 2 (2019) 1–12](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0010).

11. [G.R. Li, L. Liu, X.Y. Li, Y.F. Du, Z.H. Song, X.H. Wu, The potential of cognitive-inspired neural network modeling framework for computer vision, Adv. Sci. (2025)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0011) [e07730](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0011).

12. [Y.T. Chen, S.F. Chen, Localizing plucking points of tea leaves using deep](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0012) [convolutional neural networks, Comput. Electron. Agric. 171 (2020) 105298](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0012).

13. [Z.Y. Pan, J.N. Gu, W.B. Wang, X.L. Fang, Z.L. Xia, Q.H. Wang, M.N. Wang, Picking](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0013) [point identification and localization method based on swin-transformer for high-quality tea, J. King Saud Univ.-Com. 36 (10) (2024) 102262](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0013).

14. [H.L. Yang, L. Chen, Z.B. Ma, M.T. Chen, Y. Zhong, F. Deng, M.Z. Li, Computer](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0014) [vision-based high-quality tea automatic plucking robot using delta parallel](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0014) [manipulator, Comput. Electron. Agric. 181 (2021) 105946](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0014).

15. [X.P. Fan, T. Sun, X.J. Chai, J.P. Zhou, YOLO-WDNet: a lightweight and accurate](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0015) [model for weeds detection in cotton field, Comput. Electron. Agric. 225 (2024)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0015) [109317](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0015).

16. [H.L. Yang, L. Chen, M.T. Chen, Z.B. Ma, F. Deng, M.Z. Li, Tender tea shoots](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0016) [recognition and positioning for picking robot using improved YOLO-V3 model,](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0016) [Access 7 (2019) 180998–181011](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0016).

17. [W.K. Xu, L.G. Zhao, J. Li, S.Q. Shang, X.P. Ding, T.W. Wang, Detection and](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0017)

> [classification of tea buds based on deep learning, Comput. Electron. Agric. 192](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0017) [(2022) 106547](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0017).

18. [T.C. Chen, H.X. Li, J.Z. Chen, Z.H. Zeng, C.Y. Han, W.B. Wu, Detection network for](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0018) [multi-size and multi-target tea bud leaves in the field of view via improved](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0018) [YOLOv7, Comput. Electron. Agric. 218 (2024) 108700](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0018).

19. [Y. Song, Z.Q. Zheng, H. Zhang, Z.Y. Liu, L. Chen, J.M. Ning, Q.Y. Dai, High-precision method for simultaneous tea bud and picking point detection using](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0019) [morphology heatmap labels, Appl. Eng. Agric. 41 (6) (2025) 627–641](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0019).

20. [Z.Y. Gui, J.N. Chen, Y. Li, Z.W. Chen, C.Y. Wu, C.W. Dong, A lightweight tea bud](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0020)

> [detection model based on Yolov5, Comput. Electron. Agric. 205 (2023) 107636](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0020).

21. [J. Li, J.H. Li, X. Zhao, X.H. Su, W.B. Wu, Lightweight detection networks for tea](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0021) [bud on complex agricultural environment via improved YOLO v4, Comput.](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0021) [Electron. Agric. 211 (2023) 107955](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0021).

22. [Y.X. Wu, J.N. Chen, S.K. Wu, H. Li, L.Y. He, R.M. Zhao, C.Y. Wu, An improved](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0022) [YOLOv7 network using RGB-D multi-modal feature fusion for tea shoots detection,](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0022) [Comput. Electron. Agric. 216 (2024) 108541](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0022).

23. [L. Jianqiang, L. Haoxuan, Y. Chaoran, L. Xiao, H. Jiewei, W. Haiwei, W. Liang,](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0023)

> [Y. Caijuan, Tea bud DG: a lightweight tea bud detection model based on dynamic](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0023) [detection head and adaptive loss function, Comput. Electron. Agric. 227 (2024)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0023) [109522](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0023).

24. [Y.H. Wang, J.Z. Lu, Q. Wang, Z.M. Gao, A method of identification and localization](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0024) [of tea buds based on lightweight improved YOLOV5, Front. Plant Sci. 15 (2024)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0024) [1488185](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0024).

25. [A. Wang, H. Chen, L.H. Liu, K. Chen, Z.J. Lin, J.G. Han, G.G. Ding, Yolov10: real-time end-to-end object detection, Adv. Neural Inf. Process. Syst. 37 (2024)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0025) [107984–108011](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0025).

26. [M.X. Tan, Q.V. Le, Efficientnetv2: smaller models and faster training, in:](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0026)

> [International Conference on Machine Learning, PMLR, 2021, pp. 10096–10106](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0026).

27. [H. Zhou, F.L. Luo, H.P. Zhuang, Z.Y. Weng, X.W. Gong, Z.P. Lin, Attention](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0027) [multihop graph and multiscale convolutional fusion network for hyperspectral](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0027) [image classification, IEEE Trans. Geosci. Remote Sens. 61 (2023) 1–14](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0027).

28. [Q.B. Hou, D.Q. Zhou, J.S. Feng, Coordinate attention for efficient mobile network](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0028)

> [design, IEEE Conf. Comput. Vis. Pattern Recognit. (2021) 13713–13722](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0028).

29. [Y.P. Chen, X.Y. Dai, M.C. Liu, D.D. Chen, L. Yuan, Z.C. Liu, Dynamic convolution:](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0029) [attention over convolution kernels, IEEE Conf. Comput. Vis. Pattern Recognit.](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0029) [(2020) 11030–11039](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0029).

30. <span id="_bookmark51" class="anchor"></span>Wang J.W., Xu C., Yang W., Yu L. A normalized Gaussian Wasserstein distance for

> tiny object detection. arXiv preprint arXiv 2021; 2110.13389.

31. [H.L. Xu, L. Wang, F. Chen, Advancements in electric vehicle PCB inspection:](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0031) [application of multi-scale CBAM, partial convolution, and NWD loss in YOLOv5,](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0031) [World Electr. Veh. J. 15 (1) (2024) 15](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0031).

32. [H. Huang, X.Q. Peng, X.P. Hu, W.C. Ou, Efficient object detection and recognition](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0032) [of body welding studs based on improved YOLOv7, IEEE Access 12 (2024)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0032) [41531–41541](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0032).

33. [M.X. Song, C. Liu, L.Q. Chen, L.C. Liu, J.M. Ning, C.Y. Yu, Recognition of tea buds](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0033) [based on an improved YOLOv7 model, Int. J. Agric. Biol. Eng. 17 (6) (2024)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0033) [238–244](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0033).

34. [A. Younesi, M. Ansari, M. Fazli, A. Ejlali, M. Shafique, J. Henkel, A comprehensive](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0034)

> [survey of convolutions in deep learning: applications, challenges, and future](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0034) [trends, IEEE Access 12 (2024) 41180–41218](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0034).

35. [C.L. Chen, J.Z. Lu, M.C. Zhou, J. Yi, M. Liao, Z.M. Gao, A YOLOv3-based computer](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0035)

> [vision system for identification of tea buds and the picking point, Comput.](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0035) [Electron. Agric. 198 (2022) 107116](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0035).

36. [S.L. Chen, Y.H. Liao, J. Chen, F. Lin, Improved keypoint localization network for](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0036) [tea bud based on YOLO framework, Comput. Electron. Agric. 119 (2024) 109505](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0036).

37. <span id="_bookmark58" class="anchor"></span>[B.Y. Bai, J.S. Wang, J.L. Li, L. Yu, J.T. Wen, Y.X Han, T-YOLO: a lightweight and](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0037) [efficient detection model for nutrient buds in complex tea-plantation](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0037) [environments, J. Sci. Food Agr. 104 (10) (2024) 5698–5711](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0037).

38. [C.Y. Yu, Y. Xue, L.Y. Zhang, X. An, C. Liu, L.Q Chen, YOLO-MEST: a re-](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0038)

> [parameterized multi-scale fusion model with enhanced detection head for high-accuracy tea bud detection, Inform. Process. Agr. (2025)](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0038).

39. [M.J. Wang, Y. Li, H.W. Meng, Z.W. Chen, Z.Y. Gui, Y.P. Li, C.W. Dong, Small target](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0039) [tea bud detection based on improved YOLOv5 in complex background, Front. Plant](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0039) [Sci. 15 (2024) 1393138](http://refhub.elsevier.com/S2772-3755(26)00271-6/sbref0039).
