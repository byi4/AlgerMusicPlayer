<template>
  <div v-if="userStore.user" class="personal-fm">
    <div class="title" :class="setAnimationClass('animate__fadeInLeft')">
      {{ t('comp.personalFM.title') }}
    </div>
    <div
      v-show="personalFMSongs.length > 0"
      v-loading="loading"
      class="personal-fm-content"
      :class="setAnimationClass('animate__bounceInUp')"
    >
      <div class="personal-fm-card" @click="handlePlayPersonalFM">
        <div class="fm-cover">
          <img
            :src="currentFMSong?.picUrl || '/default-cover.jpg'"
            :alt="currentFMSong?.name || 'Personal FM'"
            class="cover-image"
          />
          <div class="play-overlay">
            <i class="iconfont ri-play-fill play-icon"></i>
          </div>
        </div>
        <div class="fm-info">
          <!-- <div class="fm-title">{{ t('comp.personalFM.title') }}</div> -->
          <div class="fm-desc">{{ t('comp.personalFM.description') }}</div>
          <div v-if="currentFMSong" class="current-song">
            <div class="song-name">{{ currentFMSong.name }}</div>
            <div class="song-artist">{{ getArtistNames(currentFMSong) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { getPersonalFM } from '@/api/home';
import { usePlayerStore, useUserStore } from '@/store';
import type { SongResult } from '@/types/music';
import { setAnimationClass } from '@/utils';

const { t } = useI18n();
const playerStore = usePlayerStore();
const userStore = useUserStore();

// 私人FM歌曲列表
const personalFMSongs = ref<SongResult[]>([]);
const loading = ref(false);

// 当前FM歌曲（显示在封面上的）
const currentFMSong = computed(() => {
  return personalFMSongs.value[0] || null;
});

// 获取艺术家名称
const getArtistNames = (song: SongResult) => {
  if (song.ar && song.ar.length > 0) {
    return song.ar.map((artist) => artist.name).join('/');
  }
  if (song.artists && song.artists.length > 0) {
    return song.artists.map((artist) => artist.name).join('/');
  }
  return '';
};

// 加载私人FM
const loadPersonalFM = async () => {
  loading.value = true;
  try {
    const { data } = await getPersonalFM();
    console.log('data:', data);

    if (data && data.data && Array.isArray(data.data)) {
      // 转换数据格式以匹配SongResult接口
      personalFMSongs.value = data.data.map((item: any) => ({
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
    }
  } catch (error) {
    console.error('加载私人FM失败:', error);
  } finally {
    loading.value = false;
  }
};

// 处理点击私人FM
const handlePlayPersonalFM = () => {
  if (personalFMSongs.value.length > 0) {
    // 清空当前播放列表，设置私人FM播放列表
    playerStore.clearPlayAll();

    // 设置播放列表为私人FM歌曲
    setTimeout(() => {
      playerStore.setPlayList(personalFMSongs.value);
      // 设置私人FM模式
      playerStore.setPersonalFMMode(true);
      // 开始播放第一首歌
      playerStore.setPlayMusic(personalFMSongs.value[0]);
    }, 600);
  }
};

// 页面初始化
onMounted(() => {
  // 只有在用户登录时才加载私人FM数据
  if (userStore.user) {
    loadPersonalFM();
  }
});

// 暴露加载函数供外部调用
defineExpose({
  loadPersonalFM
});
</script>

<style lang="scss" scoped>
.title {
  @apply text-lg font-bold mb-4 text-gray-900 dark:text-white;
}

.personal-fm {
  @apply flex-auto;

  &-content {
    @apply rounded-3xl p-4 w-full border border-gray-200 dark:border-gray-700 bg-light dark:bg-black;
  }

  &-card {
    @apply flex items-center gap-4 cursor-pointer transition-all duration-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-2xl p-3;

    .fm-cover {
      @apply relative w-16 h-16 rounded-xl overflow-hidden flex-shrink-0;

      .cover-image {
        @apply w-full h-full object-cover;
      }

      .play-overlay {
        @apply absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 transition-opacity duration-300;

        .play-icon {
          @apply text-white text-2xl;
        }
      }

      &:hover .play-overlay {
        @apply opacity-100;
      }
    }

    .fm-info {
      @apply flex-1 min-w-0;

      .fm-title {
        @apply text-base font-semibold text-gray-900 dark:text-white mb-1;
      }

      .fm-desc {
        @apply text-sm text-gray-500 dark:text-gray-400 mb-2;
      }

      .current-song {
        .song-name {
          @apply text-sm font-medium text-gray-800 dark:text-gray-200 truncate mb-1;
        }

        .song-artist {
          @apply text-xs text-gray-500 dark:text-gray-400 truncate;
        }
      }
    }
  }
}
</style>
