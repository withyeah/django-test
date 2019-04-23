# from django.test import TestCase
from test_plus.test import TestCase
from django.conf import settings
from django.urls import reverse
from .models import Board
from .forms import BoardForm

# 1. setting test
class SettingsTest(TestCase):
    def test_01_settings(self):
        self.assertEqual(settings.USE_I18N, True)
        self.assertEqual(settings.USE_TZ, False)
        self.assertEqual(settings.LANGUAGE_CODE, 'ko-kr')
        self.assertEqual(settings.TIME_ZONE, 'Asia/Seoul')
        
# 2. Model test + ModelForm test
class BoardModelTest(TestCase):
    def test_01_model(self):
        # board = Board.objects.create(title='test title', content='test content')
        board = Board.objects.create(title='test title', content='test content', user_id=1)
        self.assertEqual(str(board), f'Board{board.pk}', msg='출력 값이 일치하지 않음')
        
    def test_02_test(self):
        # given
        data = {'title': '제목', 'content': '내용'}
        # when then
        self.assertEqual(BoardForm(data).is_valid(), True)
        
    def test_03_boardform_without_title(self):
        # given
        data = {'content': '내용'}
        # when then
        self.assertEqual(BoardForm(data).is_valid(), False)
        
    def test_04_boardform_without_content(self):
        data = {'title': '제목'}
        self.assertEqual(BoardForm(data).is_valid(), False)
    
# 3. View test 
class BoardViewTest(TestCase):
    # 테스트 시작할 때 깔고 들어갈 정보
    # 공통적인 given 상황을 구성하기에 유용하다.
    def setUp(self):
        self.user = self.make_user(username='test', password='godqhrdl')
    
    # given, when, then 구조
    
    # create test 에서의 포인트는 form 을 제대로 주느냐이다.
    # 가장 기본은 get_check_200
    def test_01_get_create(self):
        # given (setUp)
        # user = self.make_user(username='test', password='godqhrdl')
        # when
        with self.login(username='test', password='godqhrdl'):
            response = self.get_check_200('boards:create')
            # then
            # self.assertContains(response, '<form')
            # BoardForm을 넘겨주는지 확인(더 정확한 테스트코드)
            self.assertIsInstance(response.context['form'], BoardForm)
            
    def test_02_get_create_login_required(self):
        self.assertLoginRequired('boards:create')
        
    def test_03_post_create(self):
        # given : 사용자와 작성한 글 데이터 (setUp)
        # user = self.make_user(username='test', password='godqhrdl')
        data = {'title': 'test title', 'content': 'test content'}
        # when : 로그인을 해서 post 요청으로 해당 url 로 요청 보낸 경우
        with self.login(username='test', password='godqhrdl'):
        # then : 글이 작성되고, 페이지가 detail 로 redirect 된다.
            self.post('boards:create', data=data)
            
    def test_04_board_create_without_content(self):
        # given
        # user 는 setUp 에서 만들어짐
        data = {'title': 'test title'}
        # when
        with self.login(username='test', password='godqhrdl'):
            response = self.post('boards:create', data=data)
            self.assertContains(response, '필') 
     
    # detail 페이지가 제대로 출력되는지 확인         
    def test_05_detail_contains(self):
        # given
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        # when : 페이지가 뜹니까?
        self.get_check_200('boards:detail', board_pk=board.pk)
        # then : 내용을 불러옵니까? (더 집약적)
        self.assertResponseContains(board.title, html=False)
        self.assertResponseContains(board.content, html=False)
        
    def test_06_detail_template(self):
        # given
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        # when
        response = self.get_check_200('boards:detail', board_pk=board.pk)
        # then : 너가 띄우는 템플릿이 이 이름이 맞아?
        self.assertTemplateUsed(response, 'boards/detail.html')
    
    def test_07_get_index(self):
        # 페이지가 잘 뜨는지 확인
        # given when then
        self.get_check_200('boards:index')
        
    def test_08_index_template(self):
        # 페이지가 잘 뜨는지, 템플릿도 이름 맞는지 확인
        # when then
        response = self.get_check_200('boards:index')
        self.assertTemplateUsed(response, 'boards/index.html')
        
    def test_09_index_queryset(self):
        # given : 글 2개 작성
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        boards = Board.objects.order_by('-pk')
        # when
        response = self.get_check_200('boards:index')
        # then
        self.assertQuerysetEqual(response.context['boards'], map(repr, boards))
    
    # 에러 뜸! delete POST 로만 받게 돼있는데 get 으로 보내서    
    def test_10_delete(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='godqhrdl'):
            self.get_check_200('boards:delete', board_pk=board.pk)
        
    def test_11_dete_post(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='godqhrdl'):
            self.post('boards:delete', board_pk=board.pk)
            self.assertEqual(Board.objects.count(), 0)
            
    def test_12_delete_redirect(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='godqhrdl'):
            response = self.post('boards:delete', board_pk=board.pk)
            # then
            self.assertRedirects(response, reverse('boards:index'))
            
    def test_13_get_update(self):
        board = Board.objects.create(title='제목', content='내용', user=self.user)
        with self.login(username='test', password='godqhrdl'):
            response = self.get_check_200('boards:update', board.pk)
            self.assertEqual(response.context['form'].instance.pk, board.pk)
            
    def test_14_get_update_login_required(self):
        self.assertLoginRequired('boards:update', board_pk=1)
        