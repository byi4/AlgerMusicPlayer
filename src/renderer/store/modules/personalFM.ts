import { defineStore } from 'pinia';
import { ref } from 'vue';

import { getPersonalFM } from '@/api/home';
import type { SongResult } from '@/types/music';

/**
 * 私人FM Store
 * 负责：私人FM模式、歌曲列表、加载更多歌曲
 */
export const usePersonalFMStore = defineStore(
  'personalFM',
  () => {
    // ==================== 状态 ====================
    const isPersonalFMMode = ref(false);
    const personalFMList = ref<SongResult[]>([]);

    // ==================== Actions ====================

    /**
     * 设置私人FM模式
     */
    const setPersonalFMMode = (value: boolean) => {
      isPersonalFMMode.value = value;
      localStorage.setItem('isPersonalFMMode', JSON.stringify(value));
    };

    /**
     * 加载私人FM歌曲
     */
    const loadPersonalFMSongs = async () => {
      try {
        const { data } = await getPersonalFM();
        if (data && data.data && Array.isArray(data.data)) {
          const newSongs = data.data.map((item: any) => ({
            id: item.id,
            name: item.name,
            picUrl: item.album?.picUrl || item.al?.picUrl || '',
            ar: item.artists || item.ar || [],
            artists: item.artists || item.ar || [],
            al: item.album || item.al || {},
            album: item.album || item.al || {},
            count: 0,
            duration: item.duration || item.dt || 0,
            dt: item.duration || item.dt || 0,
            source: 'netease' as const
          }));

          // 添加到私人FM列表末尾
          personalFMList.value.push(...newSongs);

          // 保持最多20首歌
          if (personalFMList.value.length > 20) {
            personalFMList.value = personalFMList.value.slice(-20);
          }

          localStorage.setItem('personalFMList', JSON.stringify(personalFMList.value));
          return newSongs;
        }
      } catch (error) {
        console.error('加载私人FM歌曲失败:', error);
      }
      return [];
    };

    /**
     * 处理私人FM下一首
     */
    const handlePersonalFMNext = async (playList: SongResult[], playListIndex: number) => {
      try {
        // 如果当前歌曲是列表最后一首，需要获取新歌曲
        if (playListIndex >= playList.length - 1) {
          console.log('私人FM: 当前是最后一首，获取新歌曲');
          const newSongs = await loadPersonalFMSongs();
          if (newSongs.length > 0) {
            // 添加新歌曲到播放列表
            playList.push(...newSongs);
            // 移除最旧的歌曲，保持列表最多20首
            if (playList.length > 20) {
              const removeCount = playList.length - 20;
              playList.splice(0, removeCount);
              return playListIndex - removeCount + 1; // 调整索引
            }
          }
        }

        // 返回下一首的索引
        return Math.min(playListIndex + 1, playList.length - 1);
      } catch (error) {
        console.error('私人FM切换下一首出错:', error);
        return playListIndex;
      }
    };

    /**
     * 处理私人FM上一首
     */
    const handlePersonalFMPrev = (playListIndex: number) => {
      // 私人FM模式下，只能往前切歌（如果有的话）
      if (playListIndex > 0) {
        return playListIndex - 1;
      }
      console.log('私人FM: 已经是第一首，无法往前切歌');
      return playListIndex;
    };

    /**
     * 清空私人FM列表
     */
    const clearPersonalFMList = () => {
      personalFMList.value = [];
      localStorage.removeItem('personalFMList');
    };

    /**
     * 初始化私人FM状态
     */
    const initializePersonalFM = () => {
      try {
        const savedMode = localStorage.getItem('isPersonalFMMode');
        if (savedMode) {
          isPersonalFMMode.value = JSON.parse(savedMode);
        }

        const savedList = localStorage.getItem('personalFMList');
        if (savedList) {
          personalFMList.value = JSON.parse(savedList);
        }
      } catch (error) {
        console.error('初始化私人FM状态失败:', error);
      }
    };

    return {
      // 状态
      isPersonalFMMode,
      personalFMList,

      // Actions
      setPersonalFMMode,
      loadPersonalFMSongs,
      handlePersonalFMNext,
      handlePersonalFMPrev,
      clearPersonalFMList,
      initializePersonalFM
    };
  },
  {
    persist: {
      key: 'personal-fm-store',
      storage: localStorage,
      pick: ['isPersonalFMMode', 'personalFMList']
    }
  }
);
