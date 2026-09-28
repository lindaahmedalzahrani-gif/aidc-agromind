import type { Language } from '../types';

// A single dictionary drives every string in the interface.
// Add another language later by adding one more top-level key
// with the same structure.

export interface Translations {
  nav: {
    brand: string;
    diagnose: string;
    chat: string;
    about: string;
  };

  hero: {
    title: string;
    subtitle: string;
    lead: string;
    cta: string;
  };

  diagnose: {
    heading: string;
    dropzoneTitle: string;
    dropzoneHint: string;
    dropzoneFormats: string;
    changeImage: string;
    diagnoseButton: string;
    analyzing: string;
    resultTitle: string;
    crop: string;
    diseaseOrPest: string;
    health: string;
    healthy: string;
    notHealthy: string;
    healthUnknown: string;
    modelResponse: string;
    unknownTitle: string;
    unknownBody: string;
    errorTitle: string;
    errorBody: string;
    invalidTitle: string;
    invalidBody: string;
    askAboutThis: string;
    tryAgain: string;
  };

  chat: {
    heading: string;
    lead: string;
    placeholder: string;
    send: string;
    mockNotice: string;
    emptyState: string;
    contextLabel: string;
    suggestions: string[];
  };

  about: {
    heading: string;
    body: string;
    points: { title: string; body: string }[];
  };

  footer: {
    note: string;
    languageLabel: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    nav: {
      brand: 'AgroMind',
      diagnose: 'Diagnose',
      chat: 'Ask AgroMind',
      about: 'About',
    },

    hero: {
      title: 'AgroMind',
      subtitle: 'AI-powered crop disease and pest diagnosis',
      lead:
        'Upload a crop or plant photo and AgroMind will identify the crop and detect visible signs of disease or pests using our vision-language model.',
      cta: 'Upload a photo',
    },

    diagnose: {
      heading: 'Upload a plant photo',
      dropzoneTitle: 'Drop a plant photo here',
      dropzoneHint: 'or click to browse from your device',
      dropzoneFormats: 'JPG or PNG, up to 10 MB',
      changeImage: 'Choose a different photo',
      diagnoseButton: 'Diagnose',
      analyzing: 'Analyzing your photo…',
      resultTitle: 'Diagnosis',
      crop: 'Crop',
      diseaseOrPest: 'Disease / Pest',
      health: 'Health status',
      healthy: 'Healthy',
      notHealthy: 'Signs of disease or pest',
      healthUnknown: 'Not determined',
      modelResponse: 'Model response',

      unknownTitle: "AgroMind couldn't identify this",
      unknownBody:
        'Try a clearer, well-lit photo focused on the affected leaf or area.',

      errorTitle: 'AgroMind is unavailable right now',
      errorBody:
        'The diagnosis service could not be reached. Please try again shortly.',

      invalidTitle: "This file can't be used",
      invalidBody: 'Please upload a JPG or PNG image under 10 MB.',

      askAboutThis: 'Ask AgroMind about this diagnosis',
      tryAgain: 'Try again',
    },

    chat: {
      heading: 'Ask AgroMind',

      lead:
        "Ask about causes, symptoms, disease management, and crop care based on AgroMind's diagnosis.",

      placeholder: 'Ask about this diagnosis…',
      send: 'Send',

      mockNotice:
        "AgroMind's diagnosis assistant isn't connected yet — this is a preview response.",

      emptyState:
        'Diagnose a plant photo above, then ask follow-up questions about the result.',

      contextLabel: 'About this diagnosis:',

      suggestions: [
        'What causes this?',
        'How can I manage it?',
        'What symptoms should I look for?',
        'Tell me more about this crop.',
      ],
    },

    about: {
      heading: 'About AgroMind',

      body:
        'AgroMind combines vision-language models and GPU-based inference to support crop diagnosis, pest and disease identification, and diagnosis-focused agricultural assistance.',

      points: [
        {
          title: 'Vision-language diagnosis',
          body:
            'A vision-language model reads the photo directly, identifying the crop and visible signs of disease or pests without hand-built rules.',
        },

        {
          title: 'GPU-served inference',
          body:
            'The model is served on an NVIDIA RTX A6000 GPU with 48 GB of VRAM, giving us control over deployment, performance, and future improvements.',
        },

        {
          title: 'Agricultural diagnosis assistant',
          body:
            'Ask AgroMind follow-up questions about a diagnosis, including causes, symptoms, disease management, and crop care.',
        },
      ],
    },

    footer: {
      note:
        'AgroMind — AI-assisted crop diagnosis and agricultural support.',
      languageLabel: 'Language',
    },
  },

  zh: {
    nav: {
      brand: 'AgroMind',
      diagnose: '诊断',
      chat: '咨询 AgroMind',
      about: '关于',
    },

    hero: {
      title: 'AgroMind',
      subtitle: 'AI 驱动的作物病虫害诊断',

      lead:
        '上传作物或植物照片，AgroMind 将识别作物，并使用我们的视觉语言模型检测可见的病害或虫害迹象。',

      cta: '上传照片',
    },

    diagnose: {
      heading: '上传植物照片',
      dropzoneTitle: '将植物照片拖放至此',
      dropzoneHint: '或点击从设备中选择',
      dropzoneFormats: '支持 JPG 或 PNG 格式，最大 10 MB',
      changeImage: '更换照片',
      diagnoseButton: '开始诊断',
      analyzing: '正在分析照片…',
      resultTitle: '诊断结果',
      crop: '作物',
      diseaseOrPest: '病害 / 虫害',
      health: '健康状态',
      healthy: '健康',
      notHealthy: '存在病害或虫害迹象',
      healthUnknown: '未能判定',
      modelResponse: '模型输出',

      unknownTitle: 'AgroMind 无法识别此照片',
      unknownBody:
        '请尝试上传更清晰、光线更充足，并聚焦于受影响叶片或部位的照片。',

      errorTitle: 'AgroMind 服务暂时不可用',
      errorBody: '无法连接诊断服务，请稍后重试。',

      invalidTitle: '该文件无法使用',
      invalidBody: '请上传 10 MB 以内的 JPG 或 PNG 图片。',

      askAboutThis: '就此诊断结果咨询 AgroMind',
      tryAgain: '重试',
    },

    chat: {
      heading: '咨询 AgroMind',

      lead:
        '可根据 AgroMind 的诊断结果询问病因、症状、病害管理和作物护理。',

      placeholder: '询问有关此诊断的问题…',
      send: '发送',

      mockNotice:
        'AgroMind 的诊断问答助手尚未接入，当前显示的是预览回复。',

      emptyState:
        '请先在上方上传植物照片进行诊断，然后可针对诊断结果提出后续问题。',

      contextLabel: '关于此诊断：',

      suggestions: [
        '是什么原因造成的？',
        '我该如何处理？',
        '应该注意哪些症状？',
        '请进一步介绍这种作物。',
      ],
    },

    about: {
      heading: '关于 AgroMind',

      body:
        'AgroMind 结合视觉语言模型与基于 GPU 的推理，为作物诊断、病虫害识别以及诊断相关的农业辅助提供支持。',

      points: [
        {
          title: '视觉语言诊断',
          body:
            '视觉语言模型直接读取照片，无需人工规则即可识别作物，并检测可见的病害或虫害迹象。',
        },

        {
          title: 'GPU 推理服务',
          body:
            '模型部署在配备 48 GB 显存的 NVIDIA RTX A6000 GPU 上，使我们能够自主控制部署、性能以及后续改进。',
        },

        {
          title: '农业诊断助手',
          body:
            '可针对 AgroMind 的诊断结果进一步询问病因、症状、病害管理和作物护理。',
        },
      ],
    },

    footer: {
      note: 'AgroMind — AI 辅助作物诊断与农业支持。',
      languageLabel: '语言',
    },
  },
};