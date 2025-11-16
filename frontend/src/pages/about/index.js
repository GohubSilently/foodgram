import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = ({ updateOrders, orders }) => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Привет!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Что это за сайт?</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Этот проект создан во время обучения в Яндекс Практикуме и полностью разработан самостоятельно.
            </p>
            <p className={styles.textItem}>
              Цель сайта — позволить пользователям создавать и хранить рецепты онлайн, скачивать список необходимых продуктов, просматривать рецепты друзей и добавлять любимые блюда в избранное.
            </p>
            <p className={styles.textItem}>
              Для полного доступа к функционалу нужна регистрация. Проверка email не выполняется — можно использовать любой адрес.
            </p>
            <p className={styles.textItem}>
              Делитесь любимыми рецептами и наслаждайтесь готовкой!
            </p>
          </div>
        </div>
        <aside>
          <h2 className={styles.additionalTitle}>
            Ссылки
          </h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Код проекта находится тут - <a href="https://github.com/GohubSilently" className={styles.textLink}>Github</a>
            </p>
            <p className={styles.textItem}>
              Автор проекта: <a href="https://t.me/gohub1" className={styles.textLink}>Vadim Khalin</a>
            </p>
          </div>
        </aside>
      </div>
      
    </Container>
  </Main>
}

export default About

